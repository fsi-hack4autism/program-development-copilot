# Program Development Copilot
This repository is hosted as a part of FSI Hackathon for Autism (https://github.com/fsi-hack4autism)

## Objective: Assist the BCBA design a program specifically tailored for each child
A BCBA (Board Certified Behavior Analyst) designs a program specifically for each child based on individualized treatment plan. It will center around the activitie the child enjoys and responds to. The objective is to have specific tasks for the child to complete with a certain level of fluency. This needs to take into account previous assessments, observations, and progress markers. It will be based on the ABLLS-R methodology

### Sample Scenarios
* The co-pilot will be able to ingest past program summaries in multi-modal form - videos, notes (digitized and undigitized), voide recordings, etc
* The copilot will be connected to current and past research and methodologies that will help assess and evaluate the patient and treatment plan
* Based on these, the co-pilot will place the child in a cohort of other children with similar assessments and markers
* Based on past successes of children in the cohort, the co-pilot will suggest a recalibrated treatment and markers (if needed) to the BCBA
* It can generate a progress summary at any given point of time


## Code repository setup
This repository will host multiple code bases to ingest past program summaries - uploaded by the BCBA (Board Certified Behavioral Analyst) - as well as the ability to generate a treatment plan. Largely, the repository will contain projects in the following areas:
### Data ingestion
* Focus is on capturing and normalizing the data for further use
* Data can be captured in a multimodal format - audio, video, and other formats. 
* Input can be in various languages. 
Note: Create all projects in a folder under https://github.com/fsi-hack4autism/program-development-copilot/tree/main/data-ingestion
### Copilot creation
* Focus is on using a copilot to generate a treatment plan
  * This module will specifically look for markers to place the child in a cohort of other children
  * The copilot will assist through various interfaces - summary reports, chatbots, indicators to watch for, etc.
Note: Create all projects in a folder under https://github.com/fsi-hack4autism/program-development-copilot/tree/main/copilot
