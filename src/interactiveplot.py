from flask import Flask, render_template, url_for
import pandas as pd
import plotly.express as px
import json
import plotly.graph_objects as go

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scatter')
def scatter():
    # Load JSON data
    json_file = './LebronData/lebron_james_processed.json'
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Convert JSON to DataFrame (if applicable)
    df = pd.DataFrame(data)
    df = df.sort_values(by=["Minutes", "FG"])

    # Create plot
    fig = px.scatter(df, x="Minutes", y="FG")  # Customize as needed
    graph_html = fig.to_html(full_html=False)

    return render_template('scatter.html', plot=graph_html)


@app.route('/GOAT')
def goat():
    image_url = url_for('static', filename='lebonbon.jpeg')
    return render_template('goat.html', image_url=image_url)

@app.route('/heatmap')
def heatmap():

    json_file = './LebronData/lebron_james_processed.json'
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Convert JSON to DataFrame
    df = pd.DataFrame(data)

    def convert_minutes(minute_str):
        if isinstance(minute_str, str):
            try:
                minutes, seconds = minute_str.split(':')
                return int(minutes) + int(seconds) / 60
            except ValueError:
                return float('nan')  # Return NaN if there's an error in conversion
        return float(minute_str)  # In case it's already numeric or NaN

    # Apply conversion to the 'Minutes' column
    df['Minutes'] = df['Minutes'].apply(convert_minutes)

    # Convert other columns to numeric values and replace any empty strings with NaN
    df[['Points', 'Assists', 'Rebounds', 'FG', 'FGA', '3P', '3PA', 'FT Percentage', '3P Percentage']] = \
        df[['Points', 'Assists', 'Rebounds', 'FG', 'FGA', '3P', '3PA', 'FT Percentage', '3P Percentage']].replace('', pd.NA)
    
    # Convert columns to numeric values
    df['Points'] = pd.to_numeric(df['Points'], errors='coerce')
    df['Assists'] = pd.to_numeric(df['Assists'], errors='coerce')
    df['Rebounds'] = pd.to_numeric(df['Rebounds'], errors='coerce')
    df['FG'] = pd.to_numeric(df['FG'], errors='coerce')
    df['FGA'] = pd.to_numeric(df['FGA'], errors='coerce')

    # Drop rows with NaN values in the relevant columns
    df = df.dropna(subset=['Assists', 'Rebounds', 'Minutes', 'FG'])

    df['Minutes_bin'] = pd.cut(df['Minutes'], bins=[0, 3, 5, 8, 10, 13, 15, 18, 20, 23, 25, 28, 30, 33, 35, 38, 40, 43, 45, 48, 50, 53, 55, 58, 60], right=False)

    df['Minutes_bin'] = df['Minutes_bin'].astype(str)


    # Aggregate data by 'Minutes_bin' and calculate the mean for other columns
    df_grouped = df.groupby('Minutes_bin').agg({
        'Points': 'mean', 
        'Assists': 'mean', 
        'FG': 'mean', 
        'Minutes': 'mean'
    }).reset_index()
    df_grouped['Points'] = df_grouped['Points'].fillna(0)

    # Create the bubble chart
    fig = px.scatter(df_grouped, 
                     x="Minutes", 
                     y="FG", 
                     size="Points",  # Size of bubbles will be based on Points
                     color="Assists",  # Color of the bubbles will be based on Assists (or any other stat)
                     hover_name="Minutes_bin",  # Hover information
                     log_x=False,  # Log scale for X axis (optional)
                     size_max=60,  # Max bubble size
                     title="Minutes vs FG (Bubble Chart)")

    # Adjust layout for better appearance
    fig.update_layout(
        width=900,  # Adjust width
        height=800,  # Adjust height
        title_font_size=24,  # Increase title font size
        xaxis=dict(ticks="inside", tickangle=45, tickfont_size=14),  # Improve x-axis appearance
        yaxis=dict(ticks="inside", tickangle=45, tickfont_size=14),  # Improve y-axis appearance
    )

    # Convert the Plotly figure to HTML
    graph_html = fig.to_html(full_html=False)

    # Return the HTML rendering the plot
    return render_template('heatmap.html', plot=graph_html)

@app.route('/lvj')
def lvj():
    # Load JSON data
    lebron_stats = [27.0, 7.4, 7.5, 1.5, 0.7, 50.6, 34.9]  # Example LeBron career averages
    jordan_stats = [30.1, 5.3, 6.2, 2.3, 0.8, 49.7, 32.7]  # Example Jordan career averages

    categories = ['Points', 'Assists', 'Rebounds', 'Steals', 'Blocks', 'FG%', '3P%']

    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=lebron_stats,
            name='LeBron James',
            marker=dict(color='#9d0dc9'),
            text=lebron_stats,
            textposition='auto',
        ),
        go.Bar(
            x=categories,
            y=jordan_stats,
            name='Michael Jordan',
            marker=dict(color='#c90d0d'),
            text=jordan_stats,
            textposition='auto',
        )
    ])

    # Update layout for improved look
    fig.update_layout(
        title="LeBron James vs Michael Jordan Career Averages",
        xaxis=dict(title='Statistics'),
        yaxis=dict(title='Values'),
        barmode='group',
        width=1000,  # Increased width for better appearance
        height=600,  # Increased height for better appearance
        plot_bgcolor='white',  # White background
        paper_bgcolor='#f4f4f4',  # Light gray background around the chart
        font=dict(family="Arial, sans-serif", size=16, color="black"),
        title_font=dict(size=24, color="black"),
        legend=dict(
            x=1.05,  # Move the legend outside the chart area
            y=1,
            bgcolor='rgba(255, 255, 255, 0.7)',  # Slightly transparent background for the legend
            bordercolor='rgba(0, 0, 0, 0.1)',
            font=dict(size=14, color="black")
        ),
        margin=dict(l=50, r=150, t=50, b=50)  # Add more padding to the right for the legend
    )

    # Convert the Plotly figure to HTML
    graph_html = fig.to_html(full_html=False)

    # Render the HTML template with the graph
    return render_template('lvj.html', plot=graph_html)
