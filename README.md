This repository contains assorted tools for working with and updating Zotero translators.

  * *update_compatibility.py* Updates translator compatibility based on the latest test runs.
    Essentially, this script compares the browserSupport properties of various translators against
    the tests that they passed, and marks them compatible on new platforms accordingly. At the 
    moment, there is no option to mark translators as incompatible.
    
    Syntax:
    
    ```sh
    update_compatibility.py [-h] [-d DATE]
    ```
    
    where ```DATE``` is an option argument that indicates a date from which to use test runs.
  * *update_tests.py* Replaces items for tests that did not succeed due to data mismatch with the 
    items saved from the previous test run. This means that the next time the tests run, they should
    succeed.
  
    Syntax:
    
    ```sh
    update_tests.py [-h] [-d DATE] translator [translator ...]
    ```
    
    where ```DATE``` is as above and translator is the path to a translator file.