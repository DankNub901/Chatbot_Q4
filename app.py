import streamlit as st
import pandas as pd
import tabula
import PyPDF2
from difflib import get_close_matches
import os

def extract_financial_data(pdf_file):
    """
    Extract financial data from the uploaded Q4 fiscal report PDF
    """
    try:
        # Read tables from the PDF
        tables = tabula.read_pdf(
            pdf_file,
            pages='all',
            multiple_tables=True,
            guess=False,
            pandas_options={'header': None}
        )
        
        # Initialize data structures for both sections
        financial_data = {
            'Metric': [],
            '2024_Q4': [],
            '2023_Q4': [],
            'Section': []  # To track which section each metric belongs to
        }
        
        current_section = "Financial Highlights"  # Default section
        
        for table in tables:
            # Clean the table
            table = table.fillna('')
            
            # Check for section headers to identify the current section
            for idx, row in table.iterrows():
                row_text = ' '.join(str(cell).strip() for cell in row).lower()
                
                # Check for section headers
                if 'canadian personal and business banking' in row_text:
                    current_section = "Canadian Personal and Business Banking"
                    continue
                elif 'financial highlights' in row_text:
                    current_section = "Financial Highlights"
                    continue
                
                # Skip rows that look like headers or are empty
                if not any(str(cell).strip().replace('$', '').replace(',', '').replace('.', '').isdigit() 
                          for cell in row[1:]):
                    continue
                
                # Check if this row contains financial data
                if table.shape[1] >= 3:  # At least 3 columns needed
                    metric = str(row.iloc[0]).strip()
                    if metric and not metric.isspace():
                        # Clean metric name
                        if metric.startswith('$'):
                            metric = metric[1:].strip()
                        if ' $' in metric:
                            metric = metric.split(' $')[0].strip()
                        
                        # Extract and clean values - look for the best pair of values
                        values = []
                        for col in range(1, len(row)):
                            val = clean_value(row.iloc[col])
                            if val is not None:
                                values.append(val)
                        
                        # Try to find the best pair of consecutive values
                        if len(values) >= 2:
                            # Look for the largest value which is likely the main metric
                            max_val_idx = values.index(max(values, key=lambda x: float(x.replace('%', '')) if isinstance(x, str) and '%' in x else float(x)))
                            if max_val_idx < len(values) - 1:
                                financial_data['Metric'].append(metric)
                                financial_data['2024_Q4'].append(values[max_val_idx])
                                financial_data['2023_Q4'].append(values[max_val_idx + 1])
                                financial_data['Section'].append(current_section)
        
        # Create DataFrame
        df = pd.DataFrame(financial_data)
        
        # Add derived metrics for Financial Highlights section
        highlights_df = df[df['Section'] == 'Financial Highlights']
        if not highlights_df.empty:
            if 'Total revenue' in highlights_df['Metric'].values and 'Non-interest expenses' in highlights_df['Metric'].values:
                revenue = highlights_df[highlights_df['Metric'] == 'Total revenue'].iloc[0]
                expenses = highlights_df[highlights_df['Metric'] == 'Non-interest expenses'].iloc[0]
                efficiency_ratio = (expenses['2024_Q4'] / revenue['2024_Q4'] * 100, 
                                  expenses['2023_Q4'] / revenue['2023_Q4'] * 100)
                df = pd.concat([df, pd.DataFrame({
                    'Metric': ['Efficiency ratio'],
                    '2024_Q4': [f"{efficiency_ratio[0]:.1f}%"],
                    '2023_Q4': [f"{efficiency_ratio[1]:.1f}%"],
                    'Section': ['Financial Highlights']
                })], ignore_index=True)
        
        return df
    except Exception as e:
        st.error(f"Error extracting data from PDF: {e}")
        return None

def clean_value(value):
    """
    Clean and convert values from the PDF
    """
    if pd.isna(value) or value == '':
        return None
    
    value = str(value).strip()
    
    # Handle percentage values
    if '%' in value:
        try:
            # Extract just the number before the % sign
            import re
            match = re.search(r'(-?\d+\.?\d*)\s*%', value)
            if match:
                return f"{float(match.group(1)):.1f}%"
            return None
        except:
            return None
    
    # Handle numeric values
    try:
        # Remove any currency symbols and commas
        value = value.replace('$', '').replace(',', '')
        
        # Extract the first complete number (including decimals)
        import re
        match = re.search(r'(-?\d+\.?\d*)', value)
        if match:
            # Convert to float and round to handle any floating point precision issues
            return round(float(match.group(1)), 2)
        return None
    except:
        return None

def format_answer(metric, current, previous):
    """Format the answer based on the type of value"""
    if isinstance(current, str) and '%' in current:
        return f"{metric} for Q4 2024 was {current}, compared to {previous} in Q4 2023"
    elif isinstance(current, (int, float)):
        if 'ratio' not in metric.lower() and 'per share' not in metric.lower():
            current = f"${current:,.0f} million"
            previous = f"${previous:,.0f} million"
        else:
            current = f"{current:.2f}"
            previous = f"{previous:.2f}"
    
    return f"{metric} for Q4 2024 was {current}, compared to {previous} in Q4 2023"

def find_answer(question, df):
    """
    Enhanced function using fuzzy string matching with section awareness
    """
    if df is None or df.empty:
        return "I apologize, but I couldn't extract the financial data from the PDF. Please make sure you've uploaded a valid Q4 fiscal report PDF."
    
    question = question.lower().strip()
    
    # Define common keywords and their mappings
    keyword_map = {
        'income': ['income', 'earnings', 'profit', 'revenue'],
        'revenue': ['revenue', 'income', 'earnings'],
        'expenses': ['expenses', 'costs', 'spending'],
        'eps': ['eps', 'earnings per share', 'share earnings'],
        'roe': ['roe', 'return on equity'],
        'margin': ['margin', 'interest margin'],
        'ratio': ['ratio', 'efficiency'],
        'tax': ['tax', 'taxes'],
        'personal': ['personal', 'retail', 'individual'],
        'business': ['business', 'commercial', 'corporate'],
        'banking': ['banking', 'bank']
    }
    
    # Determine which section to look in based on question
    section_to_search = None
    if any(keyword in question for keyword in ['personal', 'retail', 'business banking']):
        section_to_search = "Canadian Personal and Business Banking"
    
    # Create a list of all metrics in lowercase
    if section_to_search:
        section_df = df[df['Section'] == section_to_search]
    else:
        section_df = df
    
    metrics_lower = [m.lower() for m in section_df['Metric'].tolist()]
    
    # First try direct fuzzy matching
    matches = get_close_matches(question, metrics_lower, n=1, cutoff=0.6)
    
    if matches:
        metric_idx = metrics_lower.index(matches[0])
        row = section_df.iloc[metric_idx]
        return format_answer(row['Metric'], row['2024_Q4'], row['2023_Q4'])
    
    # If no direct match, try keyword matching
    for key, keywords in keyword_map.items():
        if any(keyword in question for keyword in keywords):
            # Find metrics containing any of these keywords
            for metric_lower, metric_original in zip(metrics_lower, section_df['Metric']):
                if any(keyword in metric_lower for keyword in keywords):
                    row = section_df[section_df['Metric'] == metric_original].iloc[0]
                    return format_answer(row['Metric'], row['2024_Q4'], row['2023_Q4'])
    
    return ("I apologize, but I couldn't find a good match for your question. You can ask about:\n"
            "1. Financial Highlights:\n"
            "   - Net income, Total revenue, ROE, EPS\n"
            "   - Non-interest expenses, Efficiency ratio\n\n"
            "2. Canadian Personal and Business Banking:\n"
            "   - Revenue, Net income\n"
            "   - Personal and business banking metrics\n"
            "   - Growth and performance indicators")

def main():
    st.title("CIBC Q4 Financial Highlights Chatbot")
    st.write("Ask me questions about CIBC's Fourth Quarter Financial Highlights!")
    
    # File uploader for PDF
    uploaded_file = st.file_uploader("Upload Q4 Fiscal Report PDF", type="pdf")
    
    # Initialize or get the DataFrame from session state
    if "df" not in st.session_state:
        st.session_state.df = None
    
    if uploaded_file is not None:
        # Save uploaded file temporarily
        with open("temp_report.pdf", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Extract data from PDF
        st.session_state.df = extract_financial_data("temp_report.pdf")
        
        # Remove temporary file
        os.remove("temp_report.pdf")
        
        if st.session_state.df is not None:
            st.success("Successfully extracted data from the PDF!")
            st.write("Extracted metrics:", st.session_state.df['Metric'].tolist())
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("What would you like to know about Q4 financial highlights?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant response
        response = find_answer(prompt, st.session_state.df)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main() 