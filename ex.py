import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import xml.etree.ElementTree as ET
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class BayesianNetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bayesian Network")
        self.graph = None
        self.node_positions = None
        self.selected_node = None
        self.observed_values = {}
        self.cpds = {}
        self.root.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, padx=20, pady=10)

        style = ttk.Style()
        style.configure('Wide.TButton', font=('Arial', 12), padding=(20, 10))

        self.load_button = ttk.Button(
            self.button_frame,
            text="Load Graph",
            command=self.load_network,
            style='Wide.TButton'
        )
        self.load_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

        self.observe_button = ttk.Button(
            self.button_frame,
            text="Make Observation",
            command=self.make_observation_mode,
            style='Wide.TButton'
        )
        self.observe_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

        self.query_button = ttk.Button(
            self.button_frame,
            text="Query",
            command=self.query_node,
            style='Wide.TButton'
        )
        self.query_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=10)

        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)

    def load_network(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if not file_path:
            return
        self.variables, self.edges, self.cpds = self.parse_xml(file_path)
        self.build_graph()
        self.plot_graph()
        messagebox.showinfo("Success", "Graph loaded successfully!")

    def parse_xml(self, file_path):
        tree = ET.parse(file_path)
        root = tree.getroot()
        network = root.find("network")
        variables = [var.get("name") for var in network.find("variables").findall("variable")]
        edges = []
        cpds = {}
        for cpd in network.find("cpds").findall("cpd"):
            variable = cpd.get("variable")
            parents = cpd.get("parents")
            probabilities = [
                list(map(float, prob.text.split(","))) for prob in cpd.find("probabilities").findall("probability")
            ]
            cpds[variable] = {"parents": parents.split(",") if parents else [], "probabilities": probabilities}
            if parents:
                edges.extend([(parent.strip(), variable) for parent in parents.split(",")])

        return variables, edges, cpds

    def build_graph(self):
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from(self.variables)
        self.graph.add_edges_from(self.edges)

    def plot_graph(self):
        self.ax.clear()

        self.node_positions = nx.spring_layout(self.graph, seed=42, k=1.0)
        node_labels = {
            node: f"{node}\n{self.observed_values.get(node, '')}" for node in self.graph.nodes
        }
        nx.draw(
            self.graph,
            pos=self.node_positions,
            ax=self.ax,
            with_labels=True,
            labels=node_labels,
            node_size=3000,
            node_color="lightblue",
            font_size=10,
            font_weight="bold",
            arrowsize=20,
        )
        self.canvas.draw()

    def make_observation_mode(self):
        self.selected_node = None
        messagebox.showinfo("Make Observation", "Click on a node to make an observation.")

    def on_canvas_click(self, event):
        if not self.selected_node and self.graph:
            for node, position in self.node_positions.items():
                distance = ((event.xdata - position[0]) ** 2 + (event.ydata - position[1]) ** 2) ** 0.5
                if distance < 0.1:
                    self.selected_node = node
                    self.show_observation_dialog(node)
                    break

    def show_observation_dialog(self, node):
        def set_observation(value):
            self.observed_values[node] = f"Observed Value: {value}"
            self.plot_graph()
            observation_window.destroy()

        observation_window = tk.Toplevel(self.root)
        observation_window.title(f"Make Observation: {node}")
        ttk.Label(observation_window, text=f"Select a value for {node}:").pack(pady=10)

        true_button = ttk.Button(
            observation_window, text="True", command=lambda: set_observation("True")
        )
        true_button.pack(side=tk.LEFT, padx=10, pady=10)

        false_button = ttk.Button(
            observation_window, text="False", command=lambda: set_observation("False")
        )
        false_button.pack(side=tk.RIGHT, padx=10, pady=10)

    def query_node(self):
        messagebox.showinfo("Query Results")

    def get_query_node(self):
        selected_node = simpledialog.askstring("Query", "Enter the node to query:")
        if selected_node not in self.graph.nodes:
            messagebox.showerror("Error", f"Node '{selected_node}' not found in the graph!")
            return None
        return selected_node

if __name__ == "__main__":
    root = tk.Tk()
    app = BayesianNetworkApp(root)
    root.mainloop()
