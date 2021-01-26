#ifndef PROBLEM_H
#define PROBLEM_H

#include "rapidjson/document.h"
#include "rapidjson/istreamwrapper.h"
#include "rapidjson/stringbuffer.h"
#include "rapidjson/writer.h"
#include "solution.h"
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <algorithm>

using namespace std;
using namespace rapidjson;

namespace NSGAII {
    class Config {
    public:
        int iteration = 1;
        int population = 500;
        int max_evaluations = 100000;
        int tournament = 5;
        double mutation = 1.0;
        double crossover = 0.8;
        double repair = 0.02;
        double xuan = 0.0;
        string problem_name;
        string dump_path;
        string result_path;

        Config(const string& file_name) {
            ifstream file(file_name);
            IStreamWrapper isw(file);
            Document d;
            d.ParseStream(isw);
            if (d.HasMember("iteration")) this->iteration = d["iteration"].GetInt();
            if (d.HasMember("population")) this->population = d["population"].GetInt();
            if (d.HasMember("max_evaluations")) this->max_evaluations = d["max_evaluations"].GetInt();
            if (d.HasMember("tournament")) this->tournament = d["tournament"].GetInt();
            if (d.HasMember("mutation")) this->mutation = d["mutation"].GetDouble();
            if (d.HasMember("crossover")) this->crossover = d["crossover"].GetDouble();
            if (d.HasMember("repair")) this->repair = d["repair"].GetDouble();
            if (d.HasMember("xuan")) this->xuan = d["xuan"].GetDouble();
            this->problem_name = d["problem_name"].GetString();
            this->dump_path = d["dump_path"].GetString();
            this->result_path = d["result_path"].GetString();

            file.close();
        }
    };

    class Problem {
    public:
        virtual void evaluate(Solution&, double bound) = 0;
        virtual vector<double> objective_ranges(double bound) = 0;
    };

    class NRP : public Problem {
    public:
        vector<vector<double>> objectives;
        vector<map<int, double>> inequations;

        NRP(const string& problem_file) {
            ifstream file(problem_file);
            IStreamWrapper isw(file);
            Document d;
            d.ParseStream(isw);

            for (const auto& objective : d["objectives"].GetArray()) {
                vector<double> obj;
                for (const auto& v : objective.GetArray()) {
                    obj.push_back(v.GetDouble());
                }
                this->objectives.push_back(obj);
            }
            int vars_num = this->objectives.at(0).size();
            for (const auto& obj : this->objectives) assert(vars_num == obj.size());

            for (const auto& inequation : d["inequations"].GetArray()) {
                map<int, double> ineq;
                for (Value::ConstMemberIterator iter = inequation.MemberBegin(); iter != inequation.MemberEnd(); ++ iter){
                    int key = stoi(iter->name.GetString());
                    double value = iter->value.GetDouble();
                    ineq.insert(pair<int, double>(key, value));
                }
                this->inequations.push_back(ineq);
            }

            file.close();
        }

        void evaluate(Solution& s, double bound) override {
            const auto& vars = s.get_variables();
            int size = vars.size();
            for (int i = 0; i < this->objectives.size(); ++ i) {
                const auto& objective = this->objectives.at(i);
                assert(objective.size() == size);
                double obj = 0.0;
                for (int k = 0; k < size; ++ k) {
                    if (vars.at(k)) obj += objective.at(k);
                }
                s.set_objective(i, obj);
            }
            for (int i = 0; i < this->inequations.size(); ++ i) {
                const auto& inequation = this->inequations.at(i);
                double cst = 0.0;
                for (auto const& [key, val] : inequation) {
                    if (key == size) {
                        cst += val;
                    } else if (vars.at(key)) {
                        cst -= val;
                    }
                }
                s.set_constraint(i, cst);
            }
            s.check_feasible();
        }

        vector<double> objective_ranges(double bound) override {
            vector<double> ranges;
            for (const auto& objective : this->objectives) {
                double up = 0.0;
                double low = 0.0;
                for (double obj : objective) {
                    if (obj > 0.0) {
                        up += obj;
                    } else {
                        low += obj;
                    }
                }
                ranges.push_back(up - low + 1.0);
            }
            return ranges;
        }
    };

    class XuanNRP : public Problem  {
    public:
        vector<double> cost;
        vector<double> profit;
        vector<double> urgency;
        vector<vector<int>> requests;
        double min_urgency;
        bool scale;

        XuanNRP(const string& problem_file) {
            ifstream file(problem_file);
            IStreamWrapper isw(file);
            Document d;
            d.ParseStream(isw);

            map<int, double> tmp_cost;
            const auto& raw_cost = d["cost"];
            for (Value::ConstMemberIterator iter = raw_cost.MemberBegin(); iter != raw_cost.MemberEnd(); ++ iter){
                int key = stoi(iter->name.GetString());
                double value = iter->value.GetDouble();
                tmp_cost.insert(pair<int, double>(key, value));
            }

            map<int, double> tmp_profit;
            const auto& raw_profit = d["profit"];
            for (Value::ConstMemberIterator iter = raw_profit.MemberBegin(); iter != raw_profit.MemberEnd(); ++ iter){
                int key = stoi(iter->name.GetString());
                double value = iter->value.GetDouble();
                tmp_profit.insert(pair<int, double>(key, value));
            }

            map<int, double> tmp_urgency;
            const auto& raw_urgency = d["urgency"];
            for (Value::ConstMemberIterator iter = raw_urgency.MemberBegin(); iter != raw_urgency.MemberEnd(); ++ iter){
                int key = stoi(iter->name.GetString());
                double value = iter->value.GetDouble();
                tmp_urgency.insert(pair<int, double>(key, value));
                min_urgency += value;
            }
            scale = false;

            // re encode requirement and customers
            int index = 0;
            vector<int> requirements;
            map<int, int> remap_req;
            assert(tmp_cost.size() == tmp_urgency.size());
            for (const auto& rpair: tmp_cost) requirements.push_back(rpair.first);
            sort(requirements.begin(), requirements.end());
            for (int requirement : requirements) {
                remap_req.insert(pair<int, int>(requirement, index));
                cost.push_back(tmp_cost.at(requirement));
                urgency.push_back(tmp_urgency.at(requirement));
                index += 1;
            }
            index = 0;
            vector<int> customers;
            map<int, int> remap_cus;
            for (const auto& cpair : tmp_profit) customers.push_back(cpair.first);
            sort(customers.begin(), customers.end());
            for (int customer : customers) {
                remap_cus.insert(pair<int, int>(customer, index));
                profit.push_back(tmp_profit.at(customer));
                index += 1;
            }

            // load requests
            const auto& raw_requests = d["request"];
            map<int, vector<int>> tmp_requests;
            for (Value::ConstMemberIterator iter = raw_requests.MemberBegin(); iter != raw_requests.MemberEnd(); ++ iter){
                int key = stoi(iter->name.GetString());
                vector<int> tmp_list;
                for (const auto& rreq : iter->value.GetArray()) {
                    tmp_list.push_back(remap_req.at(rreq.GetInt()));
                }
                tmp_requests.insert(pair<int, vector<int>>(key, tmp_list));
            }
            for (int customer : customers) {
                requests.push_back(tmp_requests.at(customer));
            }

            file.close();
        }

        void evaluate(Solution& s, double bound) override {
            const auto& vars = s.get_variables();
            int size = vars.size();
            
            double cost = 0.0;
            double profit = 0.0;
            for (int i = 0; i < size; ++ i) if (vars.at(i)) cost += this->cost.at(i);
            for (int i = 0; i < requests.size(); ++ i) {
                bool sat = true;
                for (auto req : requests.at(i)) {
                    if (!vars.at(req)) {
                        sat = false;
                        break;
                    }
                }
                if (sat) profit -= this->profit.at(i);
            }

            s.set_objective(0, profit);
            s.set_objective(1, cost);

            if (bound < -5.0) {
                // triple
                double urgency = 0.0;
                for (int i = 0; i < size; ++ i) if (vars.at(i)) urgency -= this->urgency.at(i);
                s.set_objective(2, urgency);
            } else if(bound < 0.0) {
                // binary 
            } else {
                // bincst
                double urgency = 0.0;
                for (int i = 0; i < size; ++ i) if (vars.at(i)) urgency -= this->urgency.at(i);
                if (!scale) {
                    this->min_urgency *= bound;
                    scale = true;
                }
                s.set_constraint(0, this->min_urgency - urgency);
            }
        }

        vector<double> objective_ranges(double bound) override {
            vector<double> ranges;
            double sum_cost = 0.0;
            double sum_profit = 0.0;
            std::for_each(cost.begin(), cost.end(), [&](double n){sum_cost += n;});
            std::for_each(profit.begin(), profit.end(), [&](double n){sum_profit += n;});
            ranges.push_back(sum_profit);
            ranges.push_back(sum_cost);
            if (bound < -5.0) {
                // triple
                double sum_urgency = 0.0;
                std::for_each(urgency.begin(), urgency.end(), [&](double n){sum_urgency += n;});
                ranges.push_back(sum_urgency);
            }
            return ranges;
        }
    };
}


#endif //PROBLEM_H