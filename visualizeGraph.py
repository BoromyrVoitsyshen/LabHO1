import networkx as nx
import matplotlib.pyplot as plt

# ================= ВСТАВТЕ ДАНІ З ХМАРИ СЮДИ =================

# 1. Скопіюйте сюди список MATRIX з Output (весь довгий рядок)
MATRIX = [[0, 0, 28, 74, 0, 0, 43, 22, 0, 20, 0, 0, 59, 0, 81], 
          [0, 0, 0, 96, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
          [0, 0, 0, 0, 0, 23, 8, 11, 64, 0, 0, 27, 0, 0, 0], 
          [73, 38, 0, 0, 0, 0, 0, 0, 0, 4, 0, 22, 0, 0, 0], 
          [0, 0, 0, 0, 0, 25, 0, 59, 0, 0, 100, 0, 5, 63, 0], 
          [0, 39, 0, 0, 0, 0, 0, 73, 0, 0, 65, 44, 0, 0, 0], 
          [51, 92, 0, 64, 0, 77, 0, 0, 0, 0, 33, 93, 0, 0, 0], 
          [88, 0, 49, 77, 0, 48, 0, 0, 88, 0, 54, 0, 32, 0, 0], 
          [0, 0, 23, 0, 0, 23, 64, 91, 0, 0, 24, 0, 14, 0, 0], 
          [0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 41, 0, 0, 20], 
          [0, 0, 25, 0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 49, 41], 
          [38, 0, 79, 0, 0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0], 
          [59, 0, 0, 97, 19, 0, 0, 12, 0, 60, 0, 0, 0, 0, 0], 
          [0, 72, 40, 0, 32, 0, 46, 0, 0, 22, 94, 0, 0, 0, 0], 
          [84, 0, 0, 0, 0, 82, 67, 0, 12, 56, 61, 0, 64, 49, 0]]
# (Це просто приклад, замініть його на ваш!)

# 2. Скопіюйте сюди шлях Path з Output
PATH_NODES = [0, 9, 14]
# (Це теж приклад, замініть на ваш!)

# =============================================================

def draw_exact_graph(matrix, path_nodes):
    n = len(matrix)
    G = nx.DiGraph()
    
    # Створюємо граф точно за матрицею
    for i in range(n):
        for j in range(n):
            weight = matrix[i][j]
            if weight > 0:
                G.add_edge(i, j, weight=weight)
    
    # Налаштування малювання
    pos = nx.circular_layout(G) # Можна спробувати nx.spring_layout(G, seed=42)
    
    plt.figure(figsize=(10, 8))
    
    # 1. Всі ребра (сірі)
    nx.draw_networkx_edges(G, pos, edge_color='#e0e0e0', arrows=True, width=1.0, connectionstyle="arc3,rad=0.1")
    
    # 2. Ребра шляху (червоні)
    path_edges = list(zip(path_nodes, path_nodes[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2.5, arrows=True, connectionstyle="arc3,rad=0.1")
    
    # 3. Підписи ваги (тільки на шляху)
    edge_labels = nx.get_edge_attributes(G, 'weight')
    path_labels = {edge: edge_labels[edge] for edge in path_edges if edge in edge_labels}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=path_labels, font_color='red', font_weight='bold', label_pos=0.3)

    # 4. Вузли
    # Всі звичайні
    nx.draw_networkx_nodes(G, pos, node_size=600, node_color='lightblue')
    # Шлях
    nx.draw_networkx_nodes(G, pos, nodelist=path_nodes, node_size=600, node_color='#ffaaaa')
    # Старт/Фініш
    nx.draw_networkx_nodes(G, pos, nodelist=[path_nodes[0], path_nodes[-1]], node_size=700, node_color='lightgreen')

    # 5. Номери вузлів
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")

    final_dist = sum([matrix[u][v] for u, v in path_edges])
    plt.title(f"Результат виконання PARCS (Дистанція: {final_dist})", fontsize=14)
    plt.axis('off')
    plt.show()

if __name__ == "__main__":
    draw_exact_graph(MATRIX, PATH_NODES)