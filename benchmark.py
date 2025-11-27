# -*- coding: utf-8 -*-
from __future__ import print_function
from Pyro4 import expose
import random
import time

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers

    def solve(self):
        # 1. Читаємо N (кількість вершин)
        try:
            n = self.read_input()
        except:
            n = 100 # Значення за замовчуванням
        
        # Кількість воркерів
        k = len(self.workers) if self.workers else 0
        
        print("Starting Benchmark for N=%d with %d workers..." % (n, k))

        # Засікаємо час початку (разом з генерацією, бо це частина задачі)
        start_time = time.time()

        # 2. Генерація
        matrix = self.generate_graph(n)
        
        # 3. Ініціалізація
        dist = [float('inf')] * n
        dist[0] = 0
        visited = [False] * n

        # 4. Основний цикл
        for step in xrange(n):
            # Пошук мінімуму (sequential)
            u = -1
            min_val = float('inf')
            # Оптимізація: простий цикл пошуку мінімуму
            for i in xrange(n):
                if not visited[i] and dist[i] < min_val:
                    min_val = dist[i]
                    u = i
            
            if u == -1 or dist[u] == float('inf'):
                break
            visited[u] = True

            # Паралельна частина (Map)
            if k > 0:
                row_u = matrix[u]
                mapped = []
                chunk_size = int((n + k - 1) / k)

                for i in xrange(k):
                    start_idx = i * chunk_size
                    end_idx = min((i + 1) * chunk_size, n)
                    if start_idx < n:
                        chunk = row_u[start_idx:end_idx]
                        # Асинхронний виклик
                        result = self.workers[i].calc_dist(start_idx, chunk, dist[u])
                        mapped.append(result)

                # Reduce
                for future in mapped:
                    updates = future.value
                    for target, new_dist in updates:
                        if new_dist < dist[target]:
                            dist[target] = new_dist
            else:
                pass # Якщо воркерів немає, нічого не робимо (або тут має бути послідовний код)

        # Засікаємо час завершення
        end_time = time.time()
        duration = end_time - start_time

        print("Job Finished")
        print("Time taken: %.4f seconds" % duration)

        # Формуємо короткий звіт
        result_str = "=== BENCHMARK REPORT ===\n"
        result_str += "Nodes (N): " + str(n) + "\n"
        result_str += "Workers (K): " + str(k) + "\n"
        result_str += "Execution Time: %.4f seconds\n" % duration
        result_str += "Shortest path to last node: " + str(dist[n-1]) + "\n"
        result_str += "========================\n"
        
        self.write_output(result_str)

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
        # Генеруємо рядки
        for i in xrange(n):
            row = []
            for j in xrange(n):
                if i == j:
                    row.append(0)
                # Зменшуємо ймовірність ребра для великих графів, щоб не було "каші"
                # Але для чесності залишимо 0.3 або можна зменшити до 0.1
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