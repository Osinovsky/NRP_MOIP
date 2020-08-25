SUMMARY
==========================================

The RALIC project datasets were collected by Soo Ling Lim at the University College 
London (UCL).

The datasets consist of:

   * 1714 recommendations from 61 stakeholders (OpenR)

   * 839 recommendations from 50 stakeholders (ClosedR)

   * 439 ratings from 76 stakeholders on 10 project objectives (RateP-Obj)

   * 1514 ratings from the same 76 stakeholders on 48 requirements (RateP-Req)

   * 3113 ratings from the same 76 stakeholders on 104 specific requiremnets (RateP-SReq)

   * 262 ratings from 79 stakeholders on 10 project objectives (RankP-Obj)

   * 469 ratings from the same 79 stakeholders on 51 requirements (RankP-Req)

   * 1109 ratings from the same 79 stakeholders on 132 specific requirements (RankP-SReq)

   * 276 ratings from 77 stakeholders on 10 project objectives (PointP-Obj)

   * 670 ratings from the same 77 stakeholders on 45 requirements (PointP-Req)

   * 1219 ratings from the same 77 stakeholders on 83 specific requirements (PointP-SReq)

   * 410 raw textual description of requirements provided by stakeholders (Raw-requirements)

   * stakeholders and their roles (Stakeholders-and-roles)

Recommendations are in the format <recommender, recommendee, level of influence>. 
Level of influence for OpenR is between 1 and 8 inclusive.
Level of influence for ClosedR is between 1 and 10 inclusive.

Ratings are in the format <stakeholder name, item, rating>. 
An item is either a project objective, requirement or specific requirement. 
A rating in RateP datasets is an integer i, where -1 <= i <= 5.
A rating in RankP datasets is a real number r, where 0 <= r <= 1.
A rating in PointP datasets is a real number r, where 0 < r <= 100.


The datasets were collected using questionnaires which are available at:

  http://soolinglim.wordpress.com/my-phd/


For details about data collection and data cleaning, refer to:

  Soo Ling Lim (2010). Social Networks and Collaborative Filtering in Large-Scale
  Requirements Elicitation. PhD Thesis. School of Computer Science and Engineering,
  University of New South Wales, Sydney, Australia.

  (http://www.cs.ucl.ac.uk/staff/S.Lim/phd/thesis_sooling_draft20100701.pdf)


USAGE LICENSE
==========================================

The datasets are freely available for research use under the following conditions:

  * The user must acknowledge the use of the datasets with the following reference.

    Soo Ling Lim (2010). Social Networks and Collaborative Filtering in Large-Scale
    Requirements Elicitation. PhD Thesis. School of Computer Science and Engineering,
    University of New South Wales, Sydney, Australia.

  * The user must inform the researcher at <s.lim@cs.ucl.ac.uk> on the 
    publications that may result from the use of the datasets.

  * The user may not redistribute the data without separate
    permission from the researcher.

  * The user may not use this information for any commercial or
    revenue-bearing purposes without first obtaining permission
    from the researcher.


The data is provided "as is" and the researcher cannot be held responsible for 
any errors or problems that arise from the use of the data.


If you have any further questions or comments, please contact Soo Ling Lim at
<s.lim@cs.ucl.ac.uk>.


PUBLISHED WORK THAT HAS USED THE DATASETS
==========================================

Soo Ling Lim, Daniele Quercia, Anthony Finkelstein. StakeNet: Using social networks to analyse the stakeholders of large-scale software projects, in the Proceedings of the 32nd International Conference on Software Engineering. ICSE (1) 2010: 295-304.

Soo Ling Lim, Daniele Quercia, Anthony Finkelstein. StakeSource: Harnessing the power of crowdsourcing and social networks in stakeholder analysis, in the Proceedings of the 32nd International Conference on Software Engineering. ICSE (2) 2010: 239-242.


DESCRIPTION OF DATA FILES
==========================================

OpenR.txt		tab separated list of recommender | recommendee | level of influence

ClosedR.txt		tab separated list of recommender | recommendee | level of influence

RateP-Obj.txt		tab separated list of stakeholder | item | rating

RateP-Req.txt		tab separated list of stakeholder | item | rating

RateP-SReq.txt		tab separated list of stakeholder | item | rating

RankP-Obj.txt		tab separated list of stakeholder | item | rating

RankP-Req.txt		tab separated list of stakeholder | item | rating

RankP-SReq.txt		tab separated list of stakeholder | item | rating

PointP-SReq.txt		tab separated list of stakeholder | item | rating

PointP-SReq.txt		tab separated list of stakeholder | item | rating

PointP-SReq.txt		tab separated list of stakeholder | item | rating

Req-list.txt		item ID and a short description

Req-requirements.txt	list of requirements

Stakeholders-and-roles.txt	stakeholder name | stakeholder role (stakeholder name is blank if no name is provided)


ADDITIONAL NOTES
================
In the requirements datasets, Astrid Haynes represented Bloomsbury reception staff (in ClosedR and OpenR datasets).
In the requirements datasets, Farid Sonya represented Noel Forrest (in ClosedR and OpenR datasets).