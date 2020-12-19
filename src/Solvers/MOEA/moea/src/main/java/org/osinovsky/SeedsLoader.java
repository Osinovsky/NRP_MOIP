package org.osinovsky;

import java.io.FileReader;
import java.util.ArrayList;
import java.io.BufferedReader;
import java.util.concurrent.ThreadLocalRandom;

public class SeedsLoader {
    public ArrayList<ArrayList<Boolean>> seeds = new ArrayList<ArrayList<Boolean>>();

    public ArrayList<Boolean> parseSeed(String line) {
        ArrayList<Boolean> seed = new ArrayList<>();
        for (char c : line.toCharArray()) {
            if (c == '0') {
                seed.add(false);
            } else if (c == '1') {
                seed.add(true);
            } else {
                // ignore
            }
        }
        return seed;
    }

    public SeedsLoader(String fileName) {
        try (BufferedReader br = new BufferedReader(new FileReader(fileName))) {
            String line;
            while ((line = br.readLine()) != null) {
                this.seeds.add(this.parseSeed(line));
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println(e); 
        }
    }

    public ArrayList<ArrayList<Boolean>> sample(int size) {
        ArrayList<ArrayList<Boolean>> choosenSeeds = new ArrayList<ArrayList<Boolean>>();
        ArrayList<Integer> seedIndex = new ArrayList<>();
        int seedSize = this.seeds.size();
        if (size > seedSize) {
            System.out.println("seed length not match!");
            return this.seeds;
        }
        for (int i = 0; i < size; ++ i) {
            int randomNum = ThreadLocalRandom.current().nextInt(0, seedSize);
            while(seedIndex.contains(randomNum)) {
                randomNum = ThreadLocalRandom.current().nextInt(0, seedSize);
            }
            seedIndex.add(randomNum);
            // choose that seed
            choosenSeeds.add(this.seeds.get(randomNum));
        }
        return choosenSeeds;
    }
}
