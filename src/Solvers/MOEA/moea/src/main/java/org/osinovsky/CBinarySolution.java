package org.osinovsky;

import org.uma.jmetal.solution.AbstractSolution;
import org.uma.jmetal.solution.binarysolution.BinarySolution;
import org.uma.jmetal.util.binarySet.BinarySet;
import org.uma.jmetal.util.pseudorandom.JMetalRandom;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@SuppressWarnings("serial")
public class CBinarySolution
    extends AbstractSolution<BinarySet>
    implements BinarySolution {

  protected List<Integer> bitsPerVariable ;

  /** Constructor */
  public CBinarySolution(List<Integer> bitsPerVariable, int numberOfObjectives, int numberOfConstraints) {
    super(bitsPerVariable.size(), numberOfObjectives, numberOfConstraints) ;
    this.bitsPerVariable = bitsPerVariable ;

    initializeBinaryVariables(JMetalRandom.getInstance());
  }

  /** Copy constructor */
  public CBinarySolution(CBinarySolution solution) {
    super(solution.getNumberOfVariables(), solution.getNumberOfObjectives(), solution.getNumberOfConstraints()) ;

    this.bitsPerVariable = solution.bitsPerVariable ;

    for (int i = 0; i < getNumberOfVariables(); i++) {
      setVariable(i, (BinarySet) solution.getVariable(i).clone());
    }

    for (int i = 0; i < getNumberOfObjectives(); i++) {
      setObjective(i, solution.getObjective(i)) ;
    }

    for (int i = 0; i < getNumberOfConstraints(); i++) {
      setConstraint(i, solution.getConstraint(i));
    }

    attributes = new HashMap<Object, Object>(solution.attributes) ;
  }

  private static BinarySet createNewBitSet(int numberOfBits, JMetalRandom randomGenerator) {
    BinarySet bitSet = new BinarySet(numberOfBits) ;

    for (int i = 0; i < numberOfBits; i++) {
      double rnd = randomGenerator.nextDouble() ;
      if (rnd < 0.5) {
        bitSet.set(i);
      } else {
        bitSet.clear(i);
      }
    }
    return bitSet ;
  }

  @Override
  public int getNumberOfBits(int index) {
    return getVariable(index).getBinarySetLength() ;
  }

  @Override
  public CBinarySolution copy() {
    return new CBinarySolution(this);
  }

  @Override
  public int getTotalNumberOfBits() {
    int sum = 0 ;
    for (int i = 0; i < getNumberOfVariables(); i++) {
      sum += getVariable(i).getBinarySetLength() ;
    }

    return sum ;
  }
  
  private void initializeBinaryVariables(JMetalRandom randomGenerator) {
    for (int i = 0; i < getNumberOfVariables(); i++) {
      setVariable(i, createNewBitSet(bitsPerVariable.get(i), randomGenerator));
    }
  }

	@Override
	public Map<Object, Object> getAttributes() {
		return attributes;
	}
}

