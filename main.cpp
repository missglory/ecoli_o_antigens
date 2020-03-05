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
using std::string;
using std::vector;
namespace asio = boost::asio; 

std::chrono::time_point<std::chrono::system_clock> start, end;
struct timep {
	std::chrono::duration<double> t;
	std::string s;
};
vector<timep> elapses;
void check_time(const std::string& msg) {
	elapses.push_back({ std::chrono::system_clock::now() - start, msg });
	start = std::chrono::system_clock::now();
}

vector<string> method_names = {
        "BRANCH",              //!< Selects ged::Branch.
		"BRANCH_FAST",         //!< Selects ged::BranchFast.
		"BRANCH_TIGHT",        //!< Selects ged::BranchTight.
		"BRANCH_UNIFORM",      //!< Selects ged::BranchUniform.
		"BRANCH_COMPACT",      //!< Selects ged::BranchCompact.
		"PARTITION",           //!< Selects ged::Partition.
		"HYBRID",              //!< Selects ged::Hybrid.
		"RING",                //!< Selects ged::Ring.
		"ANCHOR_AWARE_GED",    //!< Selects ged::AnchorAwareGED.
		"WALKS",               //!< Selects ged::Walks.
		"IPFP",                //!< Selects ged::IPFP
		"BIPARTITE",           //!< Selects ged::Bipartite.
		"SUBGRAPH",            //!< Selects ged::Subgraph.
		"NODE",                //!< Selects ged::Node.
		"RING_ML",             //!< Selects ged::RingML.
		"BIPARTITE_ML",        //!< Selects ged::BipartiteML.
		"REFINE",              //!< Selects ged::Refine.
		"BP_BEAM",             //!< Selects ged::BPBeam.
		"SIMULATED_ANNEALING", //!< Selects ged::SimulatedAnnealing.
		"HED",				 //!< Selects ged::HED.
		"STAR"				 //!< Selects ged::Star.
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

ged::GEDEnv<int, int, int> env;
std::mutex mtx;
vector<ged::GEDGraph::GraphID> graphs(188);
vector<string> graph_names(188);

std::ofstream log_file;

struct res {
    double upper_bound, lower_bound, runtime;
};

res tf(int j, int k, ged::Options::GEDMethod method_i) {
    env.run_method(graphs[j], graphs[k]);
    std::lock_guard<std::mu tex> lk(mtx);
    log_file << method_names[(size_t)method_i] << ":" << graph_names[j] << " : " << graph_names[k] << ". " 
        << "bounds: " << env.get_lower_bound(graphs[j], graphs[k]) << " " << env.get_upper_bound(graphs[j], graphs[k]) << "\n";
    return { env.get_lower_bound(graphs[j], graphs[k]), env.get_upper_bound(graphs[j], graphs[k]), env.get_runtime(graphs[j], graphs[k]) };
}

typedef boost::packaged_task<res> task_t;
typedef boost::shared_ptr<task_t> ptask_t;
void push_job(int j, int k, ged::Options::GEDMethod method_i, boost::asio::io_service& io_service, std::vector<boost::shared_future<res> >& pending_data) {
	ptask_t task = boost::make_shared<task_t>(boost::bind(&tf, j, k, method_i));
	boost::shared_future<res> fut(task->get_future());
	pending_data.push_back(fut);
	io_service.post(boost::bind(&task_t::operator(), task));
}


void thread_func(ged::Options::GEDMethod method_i, int lmt)
{
    env.set_method(method_i);
    start = std::chrono::system_clock::now();
// #define MULTITHREAD
#ifdef MULTITHREAD
	boost::asio::io_service io_service;
	boost::thread_group threads;
	boost::asio::io_service::work work(io_service);
    int _hc = boost::thread::hardware_concurrency();
	for (int i = 0; i < _hc; ++i)
	{
		threads.create_thread(boost::bind(&boost::asio::io_service::run,
			&io_service));
	}
	std::vector<boost::shared_future<res> > pending_data; // vector of futures
#endif
    for (int j = 0; j < lmt; j++)
        for (int k = j + 1; k < lmt; k++)
#ifndef MULTITHREAD
            tf(j,k, method_i);
#else
            push_job(j, k, method_i, io_service, pending_data);
    
    boost::wait_for_all(pending_data.begin(), pending_data.end());
#endif
    check_time("total");
    std::lock_guard<std::mutex> lk(mtx);
    log_file << "time: " << elapses.back().t.count() << " Method: " << method_names[(size_t)method_i] << "\n\n";
}


int main(int argc, const char* argv[]) {
    if (argc != 2) {
        std::cout << "usage: ./oantigens [method_id]";
        return 1;
    }
    int method_i = atoi(argv[1]);
    std::ifstream ifs;
    ifs.open("graphs_data.txt", std::ios::in);
    int num_graphs;
    ifs >> num_graphs;
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
    char* dt = ctime(&now);

    log_file.open("cpp_logs/log.txt"+std::string(dt), std::ios::out);
    // for (auto method_i : methods) {
    if (!(method_i > 0 and method_i < methods.size())) {
        std::cout << "wrong method_i\n";
        return 1;
    } else {
        string& mn = method_names[(size_t)method_i];
        string _ml = mn.substr(mn.size()-2, 2);
        if (_ml == "ML") {
            std::cout << "ML method is not available\n";
            return 1;
            // continue;
        }
        thread_func(static_cast<ged::Options::GEDMethod>(method_i), num_graphs);
    }
    log_file.close();
    ifs.close();
    return 0;
}