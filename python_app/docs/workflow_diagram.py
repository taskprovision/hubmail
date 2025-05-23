#!/usr/bin/env python3
"""
Generate a visual workflow diagram for the HubMail Python application.
This script creates a visualization of the email processing workflow using Graphviz.
"""
import os
import graphviz

def create_workflow_diagram():
    """Create a workflow diagram for the email processing pipeline."""
    # Create a new directed graph
    dot = graphviz.Digraph(comment='HubMail Email Processing Workflow')
    
    # Set graph attributes
    dot.attr(rankdir='LR', size='8,5', ratio='fill', fontname='Arial', fontsize='14')
    dot.attr('node', shape='box', style='filled', fillcolor='lightblue', 
             fontname='Arial', fontsize='12', margin='0.2,0.1')
    dot.attr('edge', fontname='Arial', fontsize='10')
    
    # Add nodes for the main workflow
    dot.node('fetch', 'Fetch New Emails\n(email_service.py)')
    dot.node('process', 'Process Emails\n(email_processor.py)')
    dot.node('analyze', 'LLM Analysis\n(llm_service.py)')
    dot.node('notify', 'Send Notifications\n(notification_service.py)')
    dot.node('mark', 'Mark as Processed\n(email_service.py)')
    
    # Add edges to connect the workflow
    dot.edge('fetch', 'process', label='emails[]')
    dot.edge('process', 'analyze', label='email')
    dot.edge('analyze', 'notify', label='analysis')
    dot.edge('notify', 'mark', label='email_id')
    
    # Add API endpoints
    dot.attr('node', shape='ellipse', style='filled', fillcolor='lightgreen')
    dot.node('api_health', '/health')
    dot.node('api_test', '/api/test-analysis')
    dot.node('api_check', '/api/check-emails')
    dot.node('api_emails', '/api/emails')
    
    # Connect API endpoints to the workflow
    dot.edge('api_test', 'analyze', style='dashed')
    dot.edge('api_check', 'fetch', style='dashed')
    
    # Create subgraph for data models
    with dot.subgraph(name='cluster_models') as c:
        c.attr(label='Data Models', style='filled', fillcolor='lightyellow')
        c.attr('node', shape='record', style='filled', fillcolor='white')
        c.node('email_model', label="Email | {id, from, subject, body, date}")
        c.node('analysis_model', label="EmailAnalysis | {id, email_id, classification, priority, summary, action_items}")
    
    # Connect data models to the workflow
    dot.edge('email_model', 'process', style='dotted')
    dot.edge('analyze', 'analysis_model', style='dotted')
    
    # Render the graph
    dot.render('hubmail_workflow', directory='docs', format='png', cleanup=True)
    dot.render('hubmail_workflow', directory='docs', format='svg', cleanup=True)
    
    print("Workflow diagrams generated in the 'docs' directory.")

if __name__ == "__main__":
    # Ensure the docs directory exists
    os.makedirs('docs', exist_ok=True)
    create_workflow_diagram()
