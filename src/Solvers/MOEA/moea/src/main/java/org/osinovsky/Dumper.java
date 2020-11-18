package org.osinovsky;

import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.util.binarySet.BinarySet;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.File;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.nio.file.Paths;
import java.io.PrintWriter;
import java.io.FileNotFoundException;
import java.io.UnsupportedEncodingException;

public class Dumper {
    public Dumper(String filePath, int index, List<BinarySolution> population, long computingTime){
        // prepare the infomation
        Map<String, Object> info = new HashMap<>();
        info.put("elapsed time", computingTime/1000.0);
        info.put("solutions found", population.size());

        ObjectMapper mapper = new ObjectMapper();
        try {
            // info file
            String fileName = Paths.get(filePath, "i_"+Integer.toString(index)+".json").toString();
            mapper.writeValue(new File(fileName), info);
        }   catch (Exception e) {
            System.out.println("An error occurred");
            e.printStackTrace();
        }

        // write the results
        try {
            String fileName = Paths.get(filePath, "s_"+Integer.toString(index)+".txt").toString();
            PrintWriter solutionFile = new PrintWriter(fileName, "UTF-8");
            // write the solutions
            for(BinarySolution solution : population) {
                double[] objs = solution.getObjectives();
                String solutionString = "(";
                boolean first = true;
                for (double obj : objs) {
                    if (!first) {
                        solutionString += ", ";
                    }else{
                        first = false;
                    }
                    solutionString += obj;
                }
                solutionString += ")";
                // write to file
                solutionFile.println(solutionString);
            }
            // close the file
            solutionFile.close();
        }  catch (FileNotFoundException e) {
            System.out.println("An error occurred #1.");
            e.printStackTrace();
        }  catch (UnsupportedEncodingException e) {
            System.out.println("An error occurred #2.");
            e.printStackTrace();
        }

        // write variables
        try {
            String fileName = Paths.get(filePath, "v_" + Integer.toString(index)+".txt").toString();
            PrintWriter variableFile = new PrintWriter(fileName, "UTF-8");
            // write the solutions
            for(BinarySolution solution : population) {
                List<BinarySet> vars = solution.getVariables();
                String variableString = "(";
                boolean first = true;
                for (BinarySet var : vars) {
                    boolean boolVar = var.get(0);
                    if (!first) {
                        variableString += ", ";
                    }else{
                        first = false;
                    }
                    if (boolVar) {
                        variableString += "1";
                    } else {
                        variableString += "0";
                    }
                }
                variableString += ")";
                // write to file
                variableFile.println(variableString);
            }
            // close the file
            variableFile.close();
        }  catch (FileNotFoundException e) {
            System.out.println("An error occurred #1.");
            e.printStackTrace();
        }  catch (UnsupportedEncodingException e) {
            System.out.println("An error occurred #2.");
            e.printStackTrace();
        }
    }
}
