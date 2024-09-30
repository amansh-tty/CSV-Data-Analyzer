import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, request, render_template, redirect, url_for

# Set up the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Helper function to check if the file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Route for file upload
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file is uploaded
        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']

        if file.filename == '':
            return 'No selected file'

        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('analyze', filename=filename))

    return render_template('upload.html')

# Route for analyzing the CSV file
@app.route('/analyze/<filename>', methods=['GET', 'POST'])
def analyze(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Initialize variables
    plot_path = None
    selected_column = None

    # Handle user input for column analysis
    if request.method == 'POST':
        selected_column = request.form.get('column')
        if selected_column and selected_column in df.columns:
            # Plot the distribution of the selected column
            plt.figure(figsize=(10, 6))
            sns.histplot(df[selected_column], kde=True)
            plt.title(f'Distribution of {selected_column}')
            plt.xlabel(selected_column)
            plt.ylabel('Frequency')
            
            # Save the plot to a static file
            plot_path = os.path.join('static', 'plot.png')
            plt.savefig(plot_path)
            plt.close()
            
    # Render the analysis page with statistics and visualizations
    return render_template('analyze.html', columns=df.columns, plot_path=plot_path, selected_column=selected_column)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
