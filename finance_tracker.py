import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json

class FinanceTracker:
    def __init__(self):
        self.categories = [
            'Housing', 'Transportation', 'Food', 'Utilities', 
            'Healthcare', 'Entertainment', 'Shopping', 'Other'
        ]
        
        # Initialize or load existing data
        if 'transactions' not in st.session_state:
            st.session_state.transactions = []
            
        if 'budgets' not in st.session_state:
            st.session_state.budgets = {cat: 0 for cat in self.categories}
    
    def add_transaction(self, date, amount, category, description):
        """Add a new transaction to the tracker."""
        transaction = {
            'date': date,
            'amount': float(amount),
            'category': category,
            'description': description
        }
        st.session_state.transactions.append(transaction)
    
    def update_budget(self, category, amount):
        """Update monthly budget for a category."""
        st.session_state.budgets[category] = float(amount)
    
    def get_monthly_spending(self, year, month):
        """Calculate total spending per category for a specific month."""
        df = pd.DataFrame(st.session_state.transactions)
        if len(df) == 0:
            return pd.DataFrame(columns=['category', 'amount'])
        
        df['date'] = pd.to_datetime(df['date'])
        monthly_mask = (df['date'].dt.year == year) & (df['date'].dt.month == month)
        monthly_spending = df[monthly_mask].groupby('category')['amount'].sum().reset_index()
        return monthly_spending
    
    def plot_monthly_comparison(self, year, month):
        """Create a bar chart comparing spending vs budget for each category."""
        monthly_spending = self.get_monthly_spending(year, month)
        
        # Prepare data for plotting
        categories = []
        spending = []
        budgets = []
        
        for category in self.categories:
            categories.append(category)
            cat_spending = monthly_spending[
                monthly_spending['category'] == category
            ]['amount'].sum() if len(monthly_spending) > 0 else 0
            spending.append(cat_spending)
            budgets.append(st.session_state.budgets[category])
        
        fig = go.Figure(data=[
            go.Bar(name='Spending', x=categories, y=spending),
            go.Bar(name='Budget', x=categories, y=budgets)
        ])
        
        fig.update_layout(
            title=f'Monthly Spending vs Budget ({datetime(year, month, 1).strftime("%B %Y")})',
            barmode='group',
            xaxis_title='Categories',
            yaxis_title='Amount ($)'
        )
        
        return fig

def main():
    st.title('Personal Finance Tracker')
    tracker = FinanceTracker()
    
    # Sidebar for adding transactions and setting budgets
    with st.sidebar:
        st.header('Add New Transaction')
        date = st.date_input('Date', datetime.now())
        amount = st.number_input('Amount ($)', min_value=0.0, step=0.01)
        category = st.selectbox('Category', tracker.categories)
        description = st.text_input('Description')
        
        if st.button('Add Transaction'):
            tracker.add_transaction(date, amount, category, description)
            st.success('Transaction added successfully!')
        
        st.header('Set Monthly Budgets')
        for category in tracker.categories:
            current_budget = st.session_state.budgets[category]
            new_budget = st.number_input(
                f'{category} Budget ($)',
                min_value=0.0,
                value=current_budget,
                key=f'budget_{category}'
            )
            tracker.update_budget(category, new_budget)
    
    # Main content area
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Display monthly comparison chart
    st.header('Monthly Spending vs Budget')
    comparison_chart = tracker.plot_monthly_comparison(current_year, current_month)
    st.plotly_chart(comparison_chart)
    
    # Display recent transactions
    st.header('Recent Transactions')
    if len(st.session_state.transactions) > 0:
        df = pd.DataFrame(st.session_state.transactions)
        df = df.sort_values('date', ascending=False)
        st.dataframe(df)
    else:
        st.info('No transactions recorded yet.')

if __name__ == '__main__':
    main()