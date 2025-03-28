import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphVisualizer:
    def __init__(self, manager, canvas):
        self.manager = manager
        self.canvas = canvas
        self.pos = None  # To stabilize layout across updates

    def show_graph(self):
        """Displays the resource allocation graph on the Tkinter canvas."""
        graph = self.manager.allocation_graph
        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)
        ax.clear()

        # Stabilize layout: Compute only if graph size changes
        if self.pos is None or len(graph.nodes()) != len(self.pos):
            self.pos = nx.spring_layout(graph, k=1.5, iterations=100)

        # Default node colors
        node_colors = ['lightblue' if n in self.manager.processes else 'lightgreen' for n in graph.nodes()]

        # Get deadlock information
        has_deadlock, deadlock_msg = self.manager.detect_deadlock()
        cycle_edges = set()
        deadlock_nodes = set()
        if has_deadlock and "Cycles:" in deadlock_msg:
            try:
                cycle_str = deadlock_msg.split("Cycles: ")[1].strip("[]")
                cycles = eval(cycle_str)  # List of edge lists
                for cycle in cycles:
                    for u, v in cycle:
                        cycle_edges.add((u, v))
                        deadlock_nodes.add(u)
                        deadlock_nodes.add(v)
            except Exception:
                cycle_edges = set()

        # Highlight deadlocked nodes (Requirement 5)
        if has_deadlock:
            node_colors = ['red' if n in deadlock_nodes else 'lightblue' if n in self.manager.processes else 'lightgreen' for n in graph.nodes()]

        nx.draw_networkx_nodes(graph, self.pos, node_color=node_colors, node_size=1000, ax=ax)
        nx.draw_networkx_labels(graph, self.pos, font_size=8, font_weight='bold', ax=ax)

        allocation_edges = [(u, v) for u, v, d in graph.edges(data=True) if d['type'] == 'allocation']
        request_edges = [(u, v) for u, v, d in graph.edges(data=True) if d['type'] == 'request']

        nx.draw_networkx_edges(graph, self.pos, edgelist=allocation_edges, edge_color='gray', arrows=True, ax=ax)
        nx.draw_networkx_edges(graph, self.pos, edgelist=request_edges, edge_color='red', style='dashed', arrows=True, ax=ax)

        ax.set_title("Resource Allocation Graph")
        ax.axis('off')

        # Clear previous content before updating visualization
        for widget in self.canvas.winfo_children():
            widget.destroy()

        canvas_widget = FigureCanvasTkAgg(fig, master=self.canvas)
        canvas_widget.draw()
        canvas_widget.get_tk_widget().pack(fill="both", expand=True)
