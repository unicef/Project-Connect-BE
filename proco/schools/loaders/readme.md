# CSV parsing process

##### 1. Uploading a file through the cms (admin panel)
1.1. Upload a file through special functionality. </br>

    https://cms.projectconnect.razortheory.com/admin/schools/fileimport/

1.2. File is uploaded to the server and the delayed task is started for parallel execution. </br>
1.3. In the process of executing the task, update the file upload status to be displayed on the upload page. </br>

##### 2. File processing
2.1. Recognizing the file format. </br>
2.2. Reading data as a list of hash tables. </br>
2.3. Country recognition is performed (with 2 options depending on the file size). </br>
2.4. Initial data validation (data types, length of values, existing value variants).


Field | Validation | Type | Max length characters | Allowed values | Link to source code |
:----:|:-----------|:----:|:---------------------:|:--------------:|:-------------------:|
school_id | Check that is within the maximum length | int | 50 | -| [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L39) |
lat | Check that value is a valid integer | int | - | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L47) |
| | Check that value isn’t negative value | | | | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L49) |
lon | Check that value is a valid integer | int | - | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L47) |
| | Check that value isn’t negative value | | | | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L49) |
educ_level | Check that is within the maximum length | str | 64 | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L57) |
name | Check that is within the maximum length | str | 255 | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L66) |
admin1 | Check that is within the maximum length | str | 100 | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L75) |
admin2 | Check that is within the maximum length | str | 100 | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L83) |
admin3 | Check that is within the maximum length | str | 100 | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L91) |
admin4 | Check that is within the maximum length | str | 100 | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L99) |
environment | Check for existing value | str | 64 | urban/rural | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L110) |
address | Check that is within the maximum length | str | 255 | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L121) |
type_school | Check that is within the maximum length | str | 64 | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L129) |
num_students | Check that value is a valid integer | int | - | ⩾0 | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L140)|
| | Check that value isn’t negative value | | | | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L145) |
num_teachers | Check that value is a valid integer | int | - | ⩾0 | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L151)|
| | Check that value isn’t negative value | | | | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L156) |
num_classroom | Check that value is a valid integer | int | - | ⩾0 | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L162)|
| | Check that value isn’t negative value | | | | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L167) |
num_latrines | Check that value is a valid integer | int | - | ⩾0 | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L173)|
| | Check that value isn’t negative value | | | | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L178) |
electricity | Check that value is compliance with the specified options | bool | - | 1/Yes/True | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L184) |
computer_lab | Check that value is compliance with the specified options | bool | - | 1/Yes/True  | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L187) |
num_computers | Check that value is a valid integer | int | - | ⩾0 | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L190)|
| | Check that value isn’t negative value | | | | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L195) |
connectivity | Check that value is compliance with the specified options | bool | - | 1/Yes/True  | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L201) |
type_connectivity | Check that is within the maximum length | str | 64 | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L203) |
speed_connectivity | Check that value is a valid float | float | - | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L214) |
coverage_availability | Check that value is compliance with the specified options | bool | - | 1/Yes/True  | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L223) |
coverage_type | Check that value is compliance with the specified options | str | 8 | No service / No / No Coverage   | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L225) |
| | Check that is within the maximum length | | | | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L230) |
| | Check that value is compliance with the specified options | | | 2G / 3G / 4G | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L238) |
latency_connectivity | Check that value is a valid integer | int | - | - | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L248) |
| | Check that value isn’t negative value | | | | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L252) |
water | Check that value is compliance with the specified options | bool | - | 1/Yes/True  | [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/validation.py#L257) |

2.5. Final validations
* To correctly identify schools in the database and update them in sequence, skip schools that have already been analyzed (duplicates of the school_id, name):</br>
Check school_id duplicates - [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/pipeline.py#L59) </br>
Check name duplicates -  [link](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/pipeline.py#L65) </br>

* Removing too close schools. Schools are searched with the same education_level if it is specified, if it is not, search for any school within a radius of 500 meters. </br>
Links: [call](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/ingest.py#L47), [source](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/pipeline.py#L146). </br>
On 10.12.2020, it was temporarily disabled and, for correct operation, replaced with a check for duplicate geolocation. </br>
[Link to validation](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/pipeline.py#L71).

* Checking that schools are within the country boundaries and removing unnecessary ones </br>
Links: [call](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/ingest.py#L55), [source](https://github.com/razortheory/project-connect-api/blob/master/proco/schools/loaders/pipeline.py#L251).

2.6. Using the data received, we create new schools or update existing ones. </br>
2.7. Update the statuses of schools. </br>
2.7. Update country status with aggregated data </br>
2.8. Mark data in the cache for the current country as not relevant. Depending on the amount of data in the country, after a while they will be updated on the map. On average, a country with 50,000 schools takes about 3 minutes.
