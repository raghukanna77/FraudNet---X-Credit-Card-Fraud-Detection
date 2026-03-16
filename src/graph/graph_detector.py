"""
Graph-based fraud detection module
Detects fraud rings and patterns using network analysis
"""

import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Any
import joblib
from collections import defaultdict

from ..utils.logger import logger
from ..utils.config import Config


class GraphFraudDetector:
    """
    Graph-based fraud ring detection
    
    Creates a transaction network with:
    - Nodes: Cards, Devices, Merchants
    - Edges: Transactions
    
    Applies graph algorithms:
    - Degree centrality
    - PageRank
    - Community detection
    """
    
    def __init__(self, config: Config = Config):
        self.config = config
        self.graph = None
        self.node_scores = {}
        self.communities = {}
        self.is_fitted = False
    
    def create_synthetic_entities(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create synthetic device and merchant IDs
        (Since original dataset doesn't have these)
        
        Args:
            df: DataFrame with transaction data
        
        Returns:
            DataFrame with synthetic entity IDs
        """
        logger.info("Creating synthetic entity IDs...")
        
        # Create card_id (use user_id if available, or create from V features)
        if 'user_id' not in df.columns:
            df['card_id'] = (df['V1'] * 1000 + df['V2'] * 100).astype(int) % 10000
        else:
            df['card_id'] = df['user_id']
        
        # Create device_id from V features that might represent device fingerprint
        df['device_id'] = (df['V3'] * 100 + df['V4'] * 50).astype(int) % 5000
        
        # Create merchant_id from V features
        df['merchant_id'] = (df['V5'] * 100 + df['V6'] * 50).astype(int) % 3000
        
        logger.info(f"Created {df['card_id'].nunique()} cards, "
                   f"{df['device_id'].nunique()} devices, "
                   f"{df['merchant_id'].nunique()} merchants")
        
        return df
    
    def build_transaction_graph(self, df: pd.DataFrame) -> nx.Graph:
        """
        Build transaction network graph
        
        Graph structure:
        - Nodes: card_id, device_id, merchant_id
        - Edges: transaction relationships
        
        Args:
            df: DataFrame with entity IDs
        
        Returns:
            NetworkX graph
        """
        logger.info("Building transaction graph...")
        
        # Ensure entity IDs exist
        if 'card_id' not in df.columns:
            df = self.create_synthetic_entities(df)
        
        # Create graph
        G = nx.Graph()
        
        # Add nodes with types
        cards = [f"card_{cid}" for cid in df['card_id'].unique()]
        devices = [f"device_{did}" for did in df['device_id'].unique()]
        merchants = [f"merchant_{mid}" for mid in df['merchant_id'].unique()]
        
        G.add_nodes_from(cards, node_type='card')
        G.add_nodes_from(devices, node_type='device')
        G.add_nodes_from(merchants, node_type='merchant')
        
        # Add edges for each transaction
        for idx, row in df.iterrows():
            card = f"card_{row['card_id']}"
            device = f"device_{row['device_id']}"
            merchant = f"merchant_{row['merchant_id']}"
            
            # Card-Device edge
            if G.has_edge(card, device):
                G[card][device]['weight'] += 1
                G[card][device]['total_amount'] += row['Amount']
            else:
                G.add_edge(card, device, weight=1, total_amount=row['Amount'])
            
            # Card-Merchant edge
            if G.has_edge(card, merchant):
                G[card][merchant]['weight'] += 1
                G[card][merchant]['total_amount'] += row['Amount']
            else:
                G.add_edge(card, merchant, weight=1, total_amount=row['Amount'])
            
            # Device-Merchant edge
            if G.has_edge(device, merchant):
                G[device][merchant]['weight'] += 1
                G[device][merchant]['total_amount'] += row['Amount']
            else:
                G.add_edge(device, merchant, weight=1, total_amount=row['Amount'])
        
        logger.info(f"Graph created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        return G
    
    def calculate_graph_features(self, G: nx.Graph) -> Dict[str, Dict[str, float]]:
        """
        Calculate graph-based features for each node
        
        Args:
            G: NetworkX graph
        
        Returns:
            Dictionary mapping node_id to features
        """
        logger.info("Calculating graph features...")
        
        # Degree centrality (how connected is this node)
        degree_centrality = nx.degree_centrality(G)
        
        # PageRank (importance in network)
        pagerank = nx.pagerank(G, alpha=self.config.GRAPH_PARAMS['pagerank_alpha'])
        
        # Betweenness centrality (how often node appears on shortest paths)
        # Only calculate for smaller graphs due to computational cost
        if G.number_of_nodes() < 10000:
            betweenness = nx.betweenness_centrality(G, k=min(100, G.number_of_nodes()))
        else:
            betweenness = {node: 0 for node in G.nodes()}
        
        # Clustering coefficient (how clustered are neighbors)
        clustering = nx.clustering(G)
        
        # Combine features
        node_features = {}
        for node in G.nodes():
            node_features[node] = {
                'degree': G.degree(node),
                'degree_centrality': degree_centrality[node],
                'pagerank': pagerank[node],
                'betweenness': betweenness[node],
                'clustering': clustering[node]
            }
        
        logger.info("Graph features calculated")
        
        return node_features
    
    def detect_communities(self, G: nx.Graph) -> Dict[str, int]:
        """
        Detect communities (potential fraud rings) using Louvain method
        
        Args:
            G: NetworkX graph
        
        Returns:
            Dictionary mapping node_id to community_id
        """
        logger.info("Detecting communities...")
        
        try:
            from networkx.algorithms import community
            # Greedy modularity communities
            communities = community.greedy_modularity_communities(G)
            
            # Map nodes to community IDs
            node_to_community = {}
            for comm_id, comm_nodes in enumerate(communities):
                for node in comm_nodes:
                    node_to_community[node] = comm_id
            
            logger.info(f"Detected {len(communities)} communities")
            
            return node_to_community
        
        except Exception as e:
            logger.warning(f"Community detection failed: {e}")
            return {node: 0 for node in G.nodes()}
    
    def fit(self, df: pd.DataFrame):
        """
        Build and analyze transaction graph
        
        Args:
            df: DataFrame with transaction data
        """
        logger.info("Fitting graph fraud detector...")
        
        # Create entity IDs if not present
        df = self.create_synthetic_entities(df)
        
        # Build graph
        self.graph = self.build_transaction_graph(df)
        
        # Calculate node features
        self.node_scores = self.calculate_graph_features(self.graph)
        
        # Detect communities
        self.communities = self.detect_communities(self.graph)
        
        self.is_fitted = True
        
        logger.info("Graph fraud detector fitted")
    
    def calculate_transaction_graph_score(
        self,
        card_id: int,
        device_id: int,
        merchant_id: int
    ) -> Dict[str, float]:
        """
        Calculate graph-based risk score for a transaction
        
        Args:
            card_id, device_id, merchant_id: Entity IDs
        
        Returns:
            Dictionary with graph risk scores
        """
        if not self.is_fitted:
            raise ValueError("Graph detector not fitted yet")
        
        # Convert to node names
        card_node = f"card_{card_id}"
        device_node = f"device_{device_id}"
        merchant_node = f"merchant_{merchant_id}"
        
        # Get features for each entity (use defaults if not in graph)
        default_features = {
            'degree': 0,
            'degree_centrality': 0,
            'pagerank': 0,
            'betweenness': 0,
            'clustering': 0
        }
        
        card_features = self.node_scores.get(card_node, default_features)
        device_features = self.node_scores.get(device_node, default_features)
        merchant_features = self.node_scores.get(merchant_node, default_features)
        
        # Calculate aggregate scores
        # High degree = more connections (could be fraud ring)
        # High PageRank = central in network (could be fraud hub)
        
        avg_degree_centrality = np.mean([
            card_features['degree_centrality'],
            device_features['degree_centrality'],
            merchant_features['degree_centrality']
        ])
        
        avg_pagerank = np.mean([
            card_features['pagerank'],
            device_features['pagerank'],
            merchant_features['pagerank']
        ])
        
        max_degree = max(
            card_features['degree'],
            device_features['degree'],
            merchant_features['degree']
        )
        
        # Check if entities are in same community (potential fraud ring)
        card_comm = self.communities.get(card_node, -1)
        device_comm = self.communities.get(device_node, -1)
        merchant_comm = self.communities.get(merchant_node, -1)
        
        same_community = int(
            card_comm == device_comm or 
            card_comm == merchant_comm or 
            device_comm == merchant_comm
        )
        
        # Combine into graph risk score (0-100 scale)
        # High values indicate potential fraud patterns
        graph_risk_score = (
            avg_degree_centrality * 30 +
            avg_pagerank * 1000 +  # PageRank is very small, scale up
            (max_degree / 100) * 20 +
            same_community * 20
        )
        
        # Clip to 0-100
        graph_risk_score = np.clip(graph_risk_score, 0, 100)
        
        return {
            'graph_risk_score': float(graph_risk_score),
            'avg_degree_centrality': float(avg_degree_centrality),
            'avg_pagerank': float(avg_pagerank),
            'max_degree': int(max_degree),
            'same_community': bool(same_community),
            'card_degree': int(card_features['degree']),
            'device_degree': int(device_features['degree']),
            'merchant_degree': int(merchant_features['degree'])
        }
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get overall graph statistics"""
        if not self.is_fitted:
            raise ValueError("Graph detector not fitted yet")
        
        return {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'num_communities': len(set(self.communities.values())),
            'density': nx.density(self.graph),
            'avg_degree': np.mean([d for n, d in self.graph.degree()])
        }
    
    def save_graph(self, path: str = None):
        """Save graph and features"""
        if path is None:
            path = self.config.MODEL_DIR / "graph_fraud_detector.pkl"
        
        joblib.dump({
            'node_scores': self.node_scores,
            'communities': self.communities,
            'is_fitted': self.is_fitted,
            'graph_stats': self.get_graph_statistics()
        }, path)
        
        logger.info(f"Graph detector saved to {path}")
    
    def load_graph(self, path: str = None):
        """Load saved graph"""
        if path is None:
            path = self.config.MODEL_DIR / "graph_fraud_detector.pkl"
        
        data = joblib.load(path)
        self.node_scores = data['node_scores']
        self.communities = data['communities']
        self.is_fitted = data['is_fitted']
        
        logger.info(f"Graph detector loaded from {path}")
