import logging
import requests
import json
import networkx as nx
import os

logger = logging.getLogger(__name__)

def extract_knowledge_graph(transcript: str, model: str = "llama3.2") -> nx.Graph:
    """
    Uses the local LLM to extract entities and relationships from the transcript text.
    Returns a networkx Graph object.
    Since it's an expensive operation, we process the first 4000 characters for MVP.
    """
    logger.info("Extracting knowledge graph entities...")
    
    truncated_text = transcript[:4000]
    
    prompt = f"""Analyze the following text and extract key entities (people, places, concepts, technologies) and their relationships.
Output ONLY a valid JSON array of relationships in this exact format:
[
  {{"source": "Entity1", "target": "Entity2", "relation": "is related to"}}
]
Return nothing else. No markdown formatting. Just the raw JSON array.

TEXT:
{truncated_text}
"""
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    G = nx.Graph()
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        result_text = response.json().get("response", "[]")
        
        try:
            relationships = json.loads(result_text)
            for rel in relationships:
                source = str(rel.get("source", "")).strip()
                target = str(rel.get("target", "")).strip()
                label = str(rel.get("relation", "")).strip()
                
                if source and target:
                    G.add_node(source)
                    G.add_node(target)
                    G.add_edge(source, target, title=label)
            logger.info(f"Extracted {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM JSON output: {result_text}")
    except Exception as e:
        logger.error(f"Error extracting graph: {e}")
        
    return G

def generate_graph_html(G: nx.Graph, output_dir: str = "downloads", filename: str = "graph.html") -> str:
    """
    A basic HTML visualizer for the graph if pyvis is not available, 
    or just returns a JSON representation. 
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    out_path = os.path.join(output_dir, filename)
    
    # We create a simple D3 or Cytoscape html since pyvis may require additional dependencies.
    # We will export graph to json and wrap it into a basic template.
    nodes = [{"data": {"id": n, "label": n}} for n in G.nodes()]
    edges = [{"data": {"source": u, "target": v, "label": d.get('title', '')}} for u, v, d in G.edges(data=True)]
    
    elements = nodes + edges
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Knowledge Graph</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.23.0/cytoscape.min.js"></script>
        <style>
            #cy {{
                width: 100%;
                height: 600px;
                display: block;
            }}
        </style>
    </head>
    <body>
        <div id="cy"></div>
        <script>
            var cy = cytoscape({{
                container: document.getElementById('cy'),
                elements: {json.dumps(elements)},
                style: [
                    {{
                        selector: 'node',
                        style: {{
                            'content': 'data(label)',
                            'background-color': '#11479e'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'label': 'data(label)',
                            'width': 2,
                            'line-color': '#9dbaea',
                            'target-arrow-color': '#9dbaea',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'font-size': '10px'
                        }}
                    }}
                ],
                layout: {{
                    name: 'cose'
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    with open(out_path, "w") as f:
        f.write(html_content)
        
    return out_path
