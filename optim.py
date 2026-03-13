import json
import heapq
import math
import datetime
import test_solution

def solve(dataset_json):
    data = json.loads(dataset_json)
    intersections = data['intersections']
    roads = data['roads']
    num_days = data['numDays']
    battery_capacity = data['batteryCapacity']

    # 1. Construction du graphe
    graph = {i['id']: [] for i in intersections}
    for road in roads:
        u, v, length = road['intersectionId1'], road['intersectionId2'], road['length']
        graph[u].append((v, length))
        if not road['isOneWay']:
            graph[v].append((u, length))

    # 2. Dijkstra standard (pour les distances)
    def dijkstra(start_node):
        distances = {i['id']: float('inf') for i in intersections}
        distances[start_node] = 0
        pq = [(0, start_node)]
        while pq:
            curr_dist, u = heapq.heappop(pq)
            if curr_dist > distances[u]: continue
            for v, weight in graph[u]:
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    heapq.heappush(pq, (distances[v], v))
        return distances

    # 3. NOUVELLE FONCTION : get_full_path (pour les points de l'itinéraire)
    def get_full_path(start, end):
        if start == end: return [start]
        distances = {i['id']: float('inf') for i in intersections}
        predecessors = {i['id']: None for i in intersections}
        distances[start] = 0
        pq = [(0, start)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > distances[u]: continue
            if u == end: break
            for v, weight in graph[u]:
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight
                    predecessors[v] = u
                    heapq.heappush(pq, (distances[v], v))
        
        path = []
        curr = end
        while curr is not None:
            path.append(curr)
            curr = predecessors[curr]
        return path[::-1]

    # 4. Trouver la borne (Optimisé)
    best_id = intersections[0]['id']
    min_score = float('inf')
    for inter in intersections[:50]: # On réduit à 50 pour Pacman
        all_dist = dijkstra(inter['id'])
        total = sum(d for d in all_dist.values() if d != float('inf'))
        score = total + (list(all_dist.values()).count(float('inf')) * 1000000)
        if score < min_score:
            min_score = score
            best_id = inter['id']
    
    station_id = best_id
    station_obj = next(i for i in intersections if i['id'] == station_id)

    # 5. Calcul des angles
    roads_with_angles = []
    for index, road in enumerate(roads):
        inter_road = next(i for i in intersections if i['id'] == road['intersectionId1'])
        angle = math.atan2(inter_road['lat'] - station_obj['lat'], inter_road['lng'] - station_obj['lng'])
        roads_with_angles.append({'road': road, 'angle': angle, 'original_id': index})
    roads_with_angles.sort(key=lambda x: x['angle'])

 # 6. SIMULATION FINALE (Optimisée pour le temps)
    itinerary = [station_id]
    current_pos = station_id
    current_battery = battery_capacity
    
    # On divise vraiment les routes en groupes (un groupe = un jour)
    roads_per_day = len(roads_with_angles) // num_days
    
   # ... (garder tout ton code identique jusqu'à la boucle des jours) ...

    for day in range(num_days):
        current_battery = battery_capacity 
        current_pos = station_id           
        
        # --- CORRECTION 1 : Ne pas rajouter station_id s'il y est déjà ---
        # (Évite les doublons qui font bondir le compteur de jours)
        
        start_idx = day * roads_per_day
        end_idx = (day + 1) * roads_per_day if day != num_days - 1 else len(roads_with_angles)
        day_roads = roads_with_angles[start_idx:end_idx]

        for item in day_roads:
            road = item['road']
            u, v = road['intersectionId1'], road['intersectionId2']
            dist_to_u = dijkstra(current_pos)[u]
            dist_back = dijkstra(v)[station_id]
            
            # --- CORRECTION 2 : Liberté le dernier jour ---
            # Si dernier jour, on ignore dist_back pour gratter du score
            limit = (dist_to_u + road['length'])
            if day < num_days - 1:
                limit += dist_back

            if current_battery >= limit:
                path_to_u = get_full_path(current_pos, u)
                itinerary.extend(path_to_u[1:])
                itinerary.append(v)
                current_battery -= (dist_to_u + road['length'])
                current_pos = v
            else:
                break
        
        # Fin de journée : retour à la borne SAUF le dernier jour
        if day < num_days - 1:
            path_home = get_full_path(current_pos, station_id)
            itinerary.extend(path_home[1:])

    return json.dumps({"chargeStationId": station_id, "itinerary": itinerary}, indent=4)

# --- BLOC D'AFFICHAGE ET TEST ---

dataset_file = "7_london" # Change le nom ici
try:
    with open(f'datasets/{dataset_file}.json', 'r') as f:
        dataset_content = f.read()

    print('---------------------------------')
    print(f'Solving {dataset_file}')
    solution_json = solve(dataset_content)
    print('Solution generated successfully.')
    print('---------------------------------')


    print("Aperçu de la solution (station choisie) :", json.loads(solution_json)["chargeStationId"])
    
    save = input('Save solution? (y/n): ')
    if save.lower() == 'y':
        date_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f'solution_{dataset_file}_{date_str}.json'
        with open(f'solutions/{file_name}', 'w') as f:
            f.write(solution_json)
        print(f'Solution saved in solutions/{file_name}')
    else:
        print('Solution not saved')

except FileNotFoundError:
    print(f"Erreur : Le fichier datasets/{dataset_file}.json est introuvable.")