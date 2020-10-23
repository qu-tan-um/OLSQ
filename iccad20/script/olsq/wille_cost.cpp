#include <iostream>
#include <list>
#include <vector>
#include <map>


class Graph 
{ 
    long long V;    // No. of vertices 
    std::list<long long> *adj; // Pointer to an array containing adjacency lists

public: 
    Graph(long long V);
    void addEdge(long long v, long long w);
    void BFS(long long s, std::map< std::vector<int>, int >& cost, std::map<long long, std::vector<int> > topi);   
}; 
  
Graph::Graph(long long V) 
{ 
    this->V = V; 
    adj = new std::list<long long>[V]; 
} 
  
void Graph::addEdge(long long v, long long w) 
{ 
    adj[v].push_back(w);
    adj[w].push_back(v);
} 

void Graph::BFS(long long s, std::map<std::vector<int>, int>& cost, std::map<long long, std::vector<int> > topi) 
{ 
    // Mark all the vertices as not visited 
    bool *visited = new bool[V]; 
    for(long long i = 0; i < V; i++) 
        visited[i] = false; 
  
    // Create a queue for BFS 
    std::list<long long> queue; 
  
    // Mark the current node as visited and enqueue it 
    visited[s] = true;
    queue.push_back(s);
    cost[topi[s]] = 0;
  
    // 'i' will be used to get all adjacent 
    // vertices of a vertex 
    std::list<long long>::iterator i; 
  
    while (!queue.empty()) { 
        // Dequeue a vertex from queue and print it 
        s = queue.front(); 
        // std::cout << s << " "; 
        queue.pop_front();
        int curr_cost = cost[topi[s]]; 
  
        // Get all adjacent vertices of the dequeued 
        // vertex s. If a adjacent has not been visited,  
        // then mark it visited and enqueue it 
        for (i = adj[s].begin(); i != adj[s].end(); ++i) 
            if (!visited[*i]) {
            	visited[*i] = true; 
                queue.push_back(*i);
                cost[topi[*i]] = curr_cost + 1;
            }           
    } 
}


std::map<std::vector<int>, int> picost;
std::map<std::vector<int>, long long> pinum;
std::map<long long, std::vector<int> > numpi;


int main() {
	int n_qubit = 5; // qubit count
	std::vector<std::vector<int> > connections = {{1, 0}, {2, 0}, {2, 1}, {3, 2}, {3, 4}, {2, 4}};


	long long n_pi = 1; // permutation count
	for (int i = 2; i <= n_qubit; ++i)
		n_pi *= i;
	std::vector<int> origin;
	for (int i = 0; i < n_qubit; ++i)
		origin.push_back(i);

	std::sort(origin.begin(), origin.end());
	long long num = 0;
	do {
		//for (int j = 0; j < origin.size(); ++j)
		//	std::cout << origin[j];
		// std::cout << ' ' << num << std::endl;
		pinum[origin] = num;
		numpi[num] = origin;
		num++;
	} while (std::next_permutation(origin.begin(), origin.end()));

	Graph pigraph(n_pi);
	for (long long i = 0; i < n_pi; ++i)
		for (long long j = i + 1; j < n_pi; ++j)
			for (int k = 0; k < connections.size(); ++k) {
				std::vector<int> tmp = numpi[i];
				int q = tmp[connections[k][0]];
				tmp[connections[k][0]] = tmp[connections[k][1]];
				tmp[connections[k][1]] = q;
				if (tmp == numpi[j]) {
					pigraph.addEdge(i, j);
					break;
				}

			}

	pigraph.BFS(0, picost, numpi);
	for (long long i = 0; i < n_pi; ++i) {
		std::vector<int> pi = numpi[i];
		std::cout << i << ' ';
		for (int j = 0; j < pi.size(); ++j)
			std::cout << pi[j];
		std::cout << ' ' << picost[pi] << std::endl;
	}
	

	return 0;
}