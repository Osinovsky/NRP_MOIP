CC = clang++
CFLAGS = -g

try:
	$(CC) -o run ./test/try.cpp
	./run
	rm -f *.o

solution_test: solution.o
	$(CC) $(CFLAGS) -o run ./test/solutionTest.cpp solution.o
	./run
	rm -f *.o

population_test: solution.o population.o
	$(CC) $(CFLAGS) -o run ./test/populationTest.cpp solution.o population.o
	./run
	rm -f *.o

problem_test: solution.o population.o
	$(CC) $(CFLAGS) -o run ./test/problemTest.cpp solution.o population.o
	./run
	rm -f *.o

dumper_test: solution.o population.o
	$(CC) $(CFLAGS) -o run ./test/dumperTest.cpp solution.o population.o
	./run
	rm -f *.o

solution.o:
	$(CC) $(CFLAGS) -c ./src/solution.cpp

population.o:
	$(CC) $(CFLAGS) -c ./src/population.cpp

NSGAII.o:
	$(CC) $(CFLAGS) -c ./src/NSGAII.cpp

.PHONY : clean
clean:
	rm -f *.o
	rm -f run