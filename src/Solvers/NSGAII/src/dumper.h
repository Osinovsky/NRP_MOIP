#ifndef DUMPER_H
#define DUMPER_H

#include "solution.h"
#include "rapidjson/document.h"
#include "rapidjson/ostreamwrapper.h"
#include "rapidjson/writer.h"
#include "rapidjson/prettywriter.h"
#include <iostream>
#include <fstream>
#include <string>
#include <iomanip>

using namespace std;
using namespace rapidjson;

namespace NSGAII {
    class Dumper {
    public:
        static void dump_json(const Document& obj, const string& file_name, bool pretty) {
            ofstream file(file_name);
            OStreamWrapper osw(file);
            if (pretty) {
                PrettyWriter<OStreamWrapper> writer(osw);
                obj.Accept(writer);
            } else {
                Writer<OStreamWrapper> writer(osw);
                obj.Accept(writer);
            }
            file.close();
        }

        static void dump_info(double time_elapsed, int solutions_found, const string& file_name) {
            Document doc;
            doc.SetObject();
            Document::AllocatorType& allocator = doc.GetAllocator();
            doc.AddMember("solutions found", time_elapsed, allocator);
            doc.AddMember("elapsed time", solutions_found, allocator);
            Dumper::dump_json(doc, file_name, false);
        }

        static void objectives_string(const vector<double>& objs, ofstream& out) {
            out << "(";
            bool first = true;
            for (double obj : objs) {
                if (first) {
                    first = false;
                } else {
                    out << ", ";
                }
                out << obj;
            }
            out << ")";
        }

        static string variables_string(const vector<bool>& vars) {
            string line = "(";
            bool first = true;
            for (bool var : vars) {
                if (first) {
                    first = false;
                } else {
                    line += ", ";
                }
                if (var) line += "1";
                else line += "0";
            }
            line += ")";
            return line;
        }

        static void dump_solutions(const vector<Solution>& solutions, const string& v_file, const string& s_file) {
            ofstream v_out(v_file);
            ofstream s_out(s_file);
            s_out << std::fixed << std::setprecision(2);
            long count = 0;
            for (const auto& solution : solutions) {
                const auto& vars = solution.get_variables();
                v_out << Dumper::variables_string(vars) << endl;
                const auto& objs = solution.get_objectives();
                Dumper::objectives_string(objs, s_out);
                s_out << endl;

                count += objs.size();
                if (count % 10000) {
                    v_out.flush();
                    s_out.flush();
                }
            }

            v_out.close();
            s_out.close();
        }
    };
}

#endif //DUMPER_H