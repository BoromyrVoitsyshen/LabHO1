from __future__ import print_function
from Pyro4 import expose
import random

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers

    def solve(self):
        # 1. Read N from input file
        n = self.read_input()
        print("Starting Dijkstra for %d nodes with %d workers" % (n, len(self.workers)))

        # 2. Generate graph
        matrix = self.generate_graph(n)
        
        # 3. Init Dijkstra
        dist = [float('inf')] * n
        dist[0] = 0
        visited = [False] * n

        # 4. Main Loop
        for step in xrange(n):
            # Sequential part: find min
            u = -1
            min_val = float('inf')
            for i in xrange(n):
                if not visited[i] and dist[i] < min_val:
                    min_val = dist[i]
                    u = i
            
            if u == -1 or dist[u] == float('inf'):
                break
            visited[u] = True

            # Parallel part: map
            row_u = matrix[u]
            mapped = []
            
            # Divide work among workers
            k = len(self.workers)
            chunk_size = int((n + k - 1) / k)

            for i in xrange(k):
                start_idx = i * chunk_size
                end_idx = min((i + 1) * chunk_size, n)
                
                if start_idx < n:
                    chunk = row_u[start_idx:end_idx]
                    # Async call to worker
                    result = self.workers[i].calc_dist(start_idx, chunk, dist[u])
                    mapped.append(result)

            # Reduce: gather results
            for future in mapped:
                updates = future.value # access the result
                for target, new_dist in updates:
                    if new_dist < dist[target]:
                        dist[target] = new_dist

        # 5. Output result
        print("Shortest distance to last node: " + str(dist[n-1]))
        self.write_output(dist[n-1])
        print("Job Finished")

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
        f.write('\n')
        f.close()