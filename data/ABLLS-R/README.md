# Data description

A brief description of what this project does and who it's for

## Description of Files

1. joinedData_assessmentStudentAssessor3_clean Anonymized.zip
  * Raw data for the ML model
  * Columns for the data
    * Anonymized data - StudentId, AssessmentId, OrganizationId, AssessorId
    * Assessment data - A1 through Z28. Different skill areas of Basic Learner Skills, specified in **ABLLS-R Guide 2018** pg 30-49
    * Assessment metadata - FirstAssessment_byStudent, **Col UC through UV**
2.  ABLLS-R Guide 2018.zip
  * Provide details about the scoring model 
  * Case studies to provide examples to show scoring for sampel assessments
  * The purpose of this model is to 
    * identify critical skills that are in need of intervention
    * provide a method for identifying a child's specific skill
    * provide a curriculum guide for an educational program for a child
3.  Normative_Report_Hackathon23.pdf
  * This was a study done with 53 students whose data is provided in the two files below
  * examplesNeuroTypical_ABLLSR.csv
    * Similar data as in the anonymized data set, but from teh study above
    * These individual assessment scores could help:
      * offer a training data set
      * characterize skill acquisition pathways
      * give timelines in skill acquisition pathways
  * normativeBenchmarkAsessments.csv
    * This provides average assessment for each category for ages 2 years, 3 years, 4 years, and 5 years
    * There is not enough data for normalized values for 1 year patients
    * Assessment score of 0-4 is normalized from 0-1 (dividing by 4)
