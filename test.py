# -*- coding: utf-8 -*-
from __future__ import print_function
from Pyro4 import expose
import random

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers

    def solve(self):
        try:
            n = self.read_input()
        except:
            n = 10

        matrix = self.generate_graph(n)
        dist = [float('inf')] * n
        parent = [-1] * n
        dist[0] = 0
        visited = [False] * n

        for step in xrange(n):
            u = -1
            min_val = float('inf')
            for i in xrange(n):
                if not visited[i] and dist[i] < min_val:
                    min_val = dist[i]
                    u = i
            
            if u == -1 or dist[u] == float('inf'):
                break
            visited[u] = True

            row_u = matrix[u]
            mapped = []
            
            k = 0
            if self.workers:
                k = len(self.workers)
            
            if k > 0:
                chunk_size = int((n + k - 1) / k)
                for i in xrange(k):
                    start_idx = i * chunk_size
                    end_idx = min((i + 1) * chunk_size, n)
                    if start_idx < n:
                        chunk = row_u[start_idx:end_idx]
                        result = self.workers[i].calc_dist(start_idx, chunk, dist[u])
                        mapped.append(result)

                for future in mapped:
                    updates = future.value
                    for target, new_dist in updates:
                        if new_dist < dist[target]:
                            dist[target] = new_dist
                            parent[target] = u
            else:
                pass

        path = self.reconstruct_path(parent, n-1)
        
        # Формуємо текст для файлу
        result_str = "Min distance: " + str(dist[n-1]) + "\n"
        result_str += "MATRIX = " + str(matrix) + "\n"
        result_str += "PATH_NODES = " + str(path) + "\n"
        
        self.write_output(result_str)

    def reconstruct_path(self, parent, target):
        if parent[target] == -1 and target != 0:
            return []
        path = []
        curr = target
        while curr != -1:
            path.append(curr)
            curr = parent[curr]
        path.reverse()
        return path

    @staticmethod
    @expose
    def calc_dist(start_idx, chunk, u_dist):
        updates = []
        for local_i, weight in enumerate(chunk):
            if weight > 0:
                target = start_idx + local_i
                new_dist = u_dist + weight
                updates.append((target, new_dist))
        return updates

    def generate_graph(self, n):
        random.seed(42)
        matrix = []
        for i in xrange(n):
            row = []
            for j in xrange(n):
                if i == j:
                    row.append(0)
                elif random.random() < 0.3:
                    row.append(random.randint(1, 100))
                else:
                    row.append(0)
            matrix.append(row)
        return matrix

    def read_input(self):
        f = open(self.input_file_name, 'r')
        line = f.readline()
        f.close()
        return int(line)

    def write_output(self, output):
        f = open(self.output_file_name, 'w')
        f.write(str(output))
        f.close()