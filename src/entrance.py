# Here is the sample on how to use this lib

from runner import Runner

# main function
if __name__ == '__main__':
    runner = Runner('realistic_e1', 'binary', 'epsilon')
    runner.run()
    runner.display()