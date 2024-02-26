import streamlit as st
import pandas as pd

def download_results(df):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='matching_pkgs.csv',
        mime='text/csv',
    )

# Assuming your data is in a file named 'default_pkg_data.xlsx' that ships with the app
default_data_path = 'pkg_data.xlsx'

# Function to load data and create a dictionary of PKGs
def create_pkg_dict(data_path):
    sheet2_df = pd.read_excel(data_path, 'Sheet1')  # Replace 'Sheet2' with actual sheet name
    return {pkg_name: set(sheet2_df[pkg_name].dropna().tolist()) for pkg_name in sheet2_df.columns}

# Load the default PKG-BOM data
pkg_dict = create_pkg_dict(default_data_path)

# Function for where used
def find_pkgs_with_bom(bom_list, pkg_dict):
    matching_pkgs = []
    bom_set = set(bom_list)
    for pkg_name, pkg_components in pkg_dict.items():
        if bom_set <= pkg_components:  # Checks if all BOMs in bom_set are in pkg_components
            matching_pkgs.append(pkg_name)
    return matching_pkgs if matching_pkgs else ["No PKG found with the specified BOM item(s)."]

# Function to find a matching PKG
def find_matching_pkg(bom_list, pkg_dict):
    bom_set = set(bom_list)
    for pkg_name, pkg_components in pkg_dict.items():
        if bom_set == pkg_components:
            return pkg_name
    return "No matching PKG found."


# Streamlit app layout
st.title("PKG Matcher")

# Radio button for the user to select input method
input_method = st.radio("Select your input method:", ('Enter Manually', 'Upload File', 'Item-Where Used'))

if input_method == 'Enter Manually':
    # Text area for user to enter BOM components, separated by newlines
    bom_input = st.text_area("Enter BOM components, each item on a new line")
    if bom_input:
        # Convert input string to a list, splitting by newlines
        bom_list = [x.strip() for x in bom_input.split('\n') if x.strip()]

        # Matching logic
        matching_pkg = find_matching_pkg(bom_list, pkg_dict)

        # Display the result
        st.write(f"The matching PKG is: {matching_pkg}")


# ... rest of the code

elif input_method == 'Upload File':
    st.markdown(
    """
    <style>
    .info-font {
        font-size:15px;
        color:#505050;
        font-style: italic;
    }
    </style>
    <div class="info-font">
    Please ensure your upload file is in the following format with each BOM component in a separate cell:
    
    **Instructions for file upload:**
    
    Please ensure your file has the following format:
    - The first row should contain headers with at least one 'BOM' column (e.g., BOM1, BOM2).
    - Each subsequent row should contain the BOM components for a single SKU.
    - Example:
        | SKU | BOM1       | BOM2       | BOM3       | BOM4       |
        |-----|------------|------------|------------|------------|
        | SKU1   | 01-97-1519 | 01-97-0451 | 01-97-0624 | 01-50-1539 |
        | SKU2   | 01-97-1519 | 01-97-0451 | 01-97-0624 | |
    
    </div>
    """, 
    unsafe_allow_html=True
)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your file with BOM components", type=['xlsx'])
    if uploaded_file:
        # Process the uploaded Excel file
        bom_df = pd.read_excel(uploaded_file)
        # Check if 'SKU' column is in the DataFrame
        if 'SKU' not in bom_df.columns:
            st.error("The uploaded file does not contain an 'SKU' column.")
        else:
            # Iterate over each row to find matching PKGs
            results = []
            for _, row in bom_df.iterrows():
                bom_list = row[1:].dropna().tolist()  # Exclude the SKU column and drop NaNs
                matching_pkg = find_matching_pkg(bom_list, pkg_dict)
                results.append({'SKU': row['SKU'], 'Matching PKG': matching_pkg})

            # Convert results to a DataFrame for display
            results_df = pd.DataFrame(results)

            # Ensure the DataFrame has the correct columns before attempting to download
            if 'SKU' in results_df.columns and 'Matching PKG' in results_df.columns:
                # Display the results in a table
                st.write(results_df)

                # Add download button for the results
                download_results(results_df[['SKU', 'Matching PKG']])
            else:
                st.error("There was an error processing the file. Please check the file format.")


elif input_method == 'Item-Where Used':
    # Text area for user to enter BOM components, each item on a new line
    bom_input = st.text_area("Enter BOM items, each item on a new line for 'Item-Where Used' search")
    if bom_input:
        # Convert input string to a list, splitting by newlines
        bom_list = [x.strip() for x in bom_input.split('\n') if x.strip()]

        # Use the new function to find PKGs where these BOMs are used
        matching_pkgs = find_pkgs_with_bom(bom_list, pkg_dict)

        # Display the result
        st.write("The following PKG files use all the specified BOM items:")
        matching_pkgs_df = pd.DataFrame(matching_pkgs, columns=['Matching PKG'])
        st.write(matching_pkgs_df)

        # Add download button for the results
        download_results(matching_pkgs_df)
