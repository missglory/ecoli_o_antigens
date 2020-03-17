#include <src/env/ged_env.hpp>
#include <iostream>
#include <thread>
#include <fstream>
#include <mutex>
#include <boost/asio/thread_pool.hpp>
#include <boost/asio/post.hpp>
#include <boost/shared_ptr.hpp>
#include <boost/make_shared.hpp>
#include <boost/thread.hpp>
#include <boost/bind.hpp>
#include <boost/asio.hpp>
#include <boost/move/move.hpp>
#include <unistd.h>
#include <stdlib.h>
#include <ctime>
#include <bits/stdc++.h> 
using std::string;
using std::vector;
using std::endl;
namespace asio = boost::asio; 

using tmpt = std::chrono::time_point<std::chrono::system_clock>;
tmpt start, end;
struct timep {
	std::chrono::duration<double> t;
	std::string s;
};
vector<timep> elapses;
void check_time(const std::string& msg, tmpt& start = start) {
	elapses.push_back({ std::chrono::system_clock::now() - start, msg });
	start = std::chrono::system_clock::now();
}

vector<string> method_names = {
        "BRANCH",              //!< Selects ged::Branch.             0
		"BRANCH_FAST",         //!< Selects ged::BranchFast.         1
		"BRANCH_TIGHT",        //!< Selects ged::BranchTight.        2
		"BRANCH_UNIFORM",      //!< Selects ged::BranchUniform.      3
		"BRANCH_COMPACT",      //!< Selects ged::BranchCompact.      4
		"PARTITION",           //!< Selects ged::Partition.          5
		"HYBRID",              //!< Selects ged::Hybrid.             6
		"RING",                //!< Selects ged::Ring.               7
		"ANCHOR_AWARE_GED",    //!< Selects ged::AnchorAwareGED.     8
		"WALKS",               //!< Selects ged::Walks.              9
		"IPFP",                //!< Selects ged::IPFP                10
		"BIPARTITE",           //!< Selects ged::Bipartite.          11
		"SUBGRAPH",            //!< Selects ged::Subgraph.           12
		"NODE",                //!< Selects ged::Node.               13
		"RING_ML",             //!< Selects ged::RingML.             14
		"BIPARTITE_ML",        //!< Selects ged::BipartiteML.        15
		"REFINE",              //!< Selects ged::Refine.             16
		"BP_BEAM",             //!< Selects ged::BPBeam.             17
		"SIMULATED_ANNEALING", //!< Selects ged::SimulatedAnnealing. 18
		"HED",				   //!< Selects ged::HED.                19
		"STAR"				   //!< Selects ged::Star.               20
};

vector<ged::Options::GEDMethod> methods = {
        ged::Options::GEDMethod::BRANCH,              //!< Selects ged::Branch.
		ged::Options::GEDMethod::BRANCH_FAST,         //!< Selects ged::BranchFast.
		ged::Options::GEDMethod::BRANCH_TIGHT,        //!< Selects ged::BranchTight.
		ged::Options::GEDMethod::BRANCH_UNIFORM,      //!< Selects ged::BranchUniform.
		ged::Options::GEDMethod::BRANCH_COMPACT,      //!< Selects ged::BranchCompact.
		ged::Options::GEDMethod::PARTITION,           //!< Selects ged::Partition.
		ged::Options::GEDMethod::HYBRID,              //!< Selects ged::Hybrid.
		ged::Options::GEDMethod::RING,                //!< Selects ged::Ring.
		ged::Options::GEDMethod::ANCHOR_AWARE_GED,    //!< Selects ged::AnchorAwareGED.
		ged::Options::GEDMethod::WALKS,               //!< Selects ged::Walks.
		ged::Options::GEDMethod::IPFP,                //!< Selects ged::IPFP
		ged::Options::GEDMethod::BIPARTITE,           //!< Selects ged::Bipartite.
		ged::Options::GEDMethod::SUBGRAPH,            //!< Selects ged::Subgraph.
		ged::Options::GEDMethod::NODE,                //!< Selects ged::Node.
		ged::Options::GEDMethod::RING_ML,             //!< Selects ged::RingML.
		ged::Options::GEDMethod::BIPARTITE_ML,        //!< Selects ged::BipartiteML.
		ged::Options::GEDMethod::REFINE,              //!< Selects ged::Refine.
		ged::Options::GEDMethod::BP_BEAM,             //!< Selects ged::BPBeam.
		ged::Options::GEDMethod::SIMULATED_ANNEALING, //!< Selects ged::SimulatedAnnealing.
		ged::Options::GEDMethod::HED,				 //!< Selects ged::HED.
		ged::Options::GEDMethod::STAR				 //!< Selects ged::Star.
};

vector<ged::Options::GEDMethod> to_calc = {
        ged::Options::GEDMethod::BRANCH,              //!< Selects ged::Branch.
		ged::Options::GEDMethod::BRANCH_FAST,         //!< Selects ged::BranchFast.
		ged::Options::GEDMethod::BRANCH_TIGHT,        //!< Selects ged::BranchTight.
		ged::Options::GEDMethod::BRANCH_UNIFORM,      //!< Selects ged::BranchUniform.
		ged::Options::GEDMethod::BRANCH_COMPACT,      //!< Selects ged::BranchCompact.
		ged::Options::GEDMethod::PARTITION,           //!< Selects ged::Partition.
		ged::Options::GEDMethod::HYBRID,              //!< Selects ged::Hybrid.
		ged::Options::GEDMethod::RING,                //!< Selects ged::Ring.
		// ged::Options::GEDMethod::ANCHOR_AWARE_GED,    //!< Selects ged::AnchorAwareGED.
		ged::Options::GEDMethod::WALKS,               //!< Selects ged::Walks.
		ged::Options::GEDMethod::IPFP,                //!< Selects ged::IPFP
		ged::Options::GEDMethod::BIPARTITE,           //!< Selects ged::Bipartite.
		ged::Options::GEDMethod::SUBGRAPH,            //!< Selects ged::Subgraph.
		ged::Options::GEDMethod::NODE,                //!< Selects ged::Node.
		// ged::Options::GEDMethod::RING_ML,             //!< Selects ged::RingML.
		// ged::Options::GEDMethod::BIPARTITE_ML,        //!< Selects ged::BipartiteML.
		ged::Options::GEDMethod::REFINE,              //!< Selects ged::Refine.
		ged::Options::GEDMethod::BP_BEAM,             //!< Selects ged::BPBeam.
		ged::Options::GEDMethod::SIMULATED_ANNEALING, //!< Selects ged::SimulatedAnnealing.
		ged::Options::GEDMethod::HED,				 //!< Selects ged::HED.
		ged::Options::GEDMethod::STAR				 //!< Selects ged::Star.
};

ged::GEDEnv<int, int, int> env;
std::mutex mtx;
vector<ged::GEDGraph::GraphID> graphs;
vector<string> graph_names;

std::ofstream log_file;

struct res {
    double lower_bound, upper_bound;
};

res tf(int j, int k, ged::Options::GEDMethod method_i, bool write_log = true) {
    env.run_method(graphs[j], graphs[k]);
    if (write_log)
    {
        check_time(std::to_string(j) + "_" + std::to_string(k));
        std::lock_guard<std::mutex> lk(mtx);
        log_file << method_names[(size_t)method_i] << ":" << graph_names[j] << " : " << graph_names[k] << ". " 
            << "bounds: " << env.get_lower_bound(graphs[j], graphs[k]) << " " << env.get_upper_bound(graphs[j], graphs[k]) << " . Time: " << elapses.back().t.count() <<"\n";
    }
    return { env.get_lower_bound(graphs[j], graphs[k]), env.get_upper_bound(graphs[j], graphs[k])};
}


vector<res> thread_func(ged::Options::GEDMethod method_i, int lmt, bool write_log = true)
{
    env.set_method(method_i);
    tmpt ttl = std::chrono::system_clock::now();
    vector<res> ret(lmt/2);
    for (int j = 0; j < lmt; j+=2)
        ret[j/2] = tf(j,j+1, method_i, write_log);
    check_time("total", ttl);
    log_file << "time: " << elapses.back().t.count() << " Method: " << method_names[(size_t)method_i] << "\n\n";
    return ret;
}


int main(int argc, const char* argv[]) {
    std::ios_base::sync_with_stdio(1);
    int batch_i=0, method_i=0;
    if (argc != 3) {
        std::cout << "usage: ./oantigens [method_id] [batch_file_num]\n";
        std::cout << "using batch 175\n";
        // return 1;
        batch_i = 174;
    } else {
        method_i = atoi(argv[1]);
        batch_i = atoi(argv[2]);
    }    
    std::cout 
        // << "Current method: " << method_names[method_i] << "\n"
        << "Batch: " << batch_i << "\n\n";
    std::ifstream ifs;

    std::string _pref = "/mnt/d/Github/oantigens/";
    
    ifs.open(_pref + "rep_data/graphs_rep_data_batch_"+std::to_string(batch_i)+".txt", std::ios::in);
    int num_graphs;
    assert(ifs.is_open());
    ifs >> num_graphs;
    graph_names.resize(num_graphs);
    graphs.resize(num_graphs);
    string graph_name = "";
    std::getline(ifs, graph_name);
    for (int i = 0; i < num_graphs; i++)
    {
        int num_nodes, num_edges;
        std::getline(ifs, graph_name);
        if (!graph_name.size()) {
            std::getline(ifs, graph_name);
        }
        graph_names[i] = graph_name;
        ifs >> num_nodes >> num_edges;
        graphs[i] = env.add_graph(graph_name);
        auto& g = graphs[i];
        for (int n = 0; n < num_nodes; n++)
        {
            int node_i, node_lbl;
            ifs >> node_i >> node_lbl;
            env.add_node(g, node_i, node_lbl);
        }
        for (int n = 0; n < num_edges; n++)
        {
            int e1, e2, edge_lbl;
            ifs >> e1 >> e2 >> edge_lbl;
            env.add_edge(g, e1, e2, edge_lbl, true);
        }
    }
    env.set_edit_costs(ged::Options::EditCosts::CONSTANT);
    env.init();

    time_t now = time(0);
    // char* dt = ctime(&now);
    tm *ltm = localtime(&now);

    std::stringstream sstream;
    sstream 
        << 1 + ltm->tm_hour << "-"//":"
        << 1 + ltm->tm_min << "-"//":"
        << 1 + ltm->tm_sec << "_"
        << ltm->tm_mday << "."
        << 1 + ltm->tm_mon<< "."
        << -100 + ltm->tm_year
        ;
    string log_time_str = sstream.str();
    string log_name = _pref+"cpp_logs/log_"+method_names[method_i]+"_batch_"+std::to_string(batch_i)+"_"+log_time_str;
    std::cout << "log file: " << log_name << endl;
    log_file.open(log_name, std::ios::out);
    
    vector<res> final_res(num_graphs/2, {0, 1e5});
    assert(num_graphs/2*2==num_graphs);

    for (auto method_i : to_calc) {
        string& mn = method_names[(size_t)method_i];
        string _ml = mn.substr(mn.size()-2, 2);
        if (_ml == "ML") {
            std::cout << "ML method is not available\n";
            return 1;
            // continue;
        }
        vector<res> mres = thread_func(static_cast<ged::Options::GEDMethod>(method_i), num_graphs);
        for (size_t i = 0; i < mres.size(); i++) {
            res& fr = final_res[i];
            fr.lower_bound = std::max(fr.lower_bound, mres[i].lower_bound);
            fr.upper_bound = std::min(fr.upper_bound, mres[i].upper_bound);
        }
    }

    log_file << "\nFINAL RESULT:\n";
    for (int i = 0; i < final_res.size(); i++) {
        log_file << graph_names[i*2] << " : " << graph_names[i*2+1] << " . bounds: " << final_res[i].lower_bound << " " << final_res[i].upper_bound << endl;
    }

    log_file.close();
    ifs.close();
    return 0;
}
