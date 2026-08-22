// ==========================================
// PredictSafe AI - JavaScript
// ==========================================


// ------------------------------------------
// CSV Upload
// ------------------------------------------

const uploadForm = document.getElementById("uploadForm");

if (uploadForm) {

    uploadForm.addEventListener("submit", function(event) {

        event.preventDefault();


        const fileInput =
            document.getElementById("csvFile");

        const message =
            document.getElementById("uploadMessage");


        if (fileInput.files.length === 0) {

            message.textContent =
                "Please select a CSV file.";

            return;
        }


        const file =
            fileInput.files[0];


        if (!file.name.toLowerCase().endsWith(".csv")) {

            message.textContent =
                "Please upload a CSV file.";

            return;
        }


        message.textContent =
            "CSV file selected successfully. Processing will be connected to the Python backend.";

    });

}



// ------------------------------------------
// Inspector Feedback
// ------------------------------------------

const feedbackForm =
    document.getElementById("feedbackForm");


if (feedbackForm) {

    feedbackForm.addEventListener(
        "submit",
        function(event) {

            event.preventDefault();


            const message =
                document.getElementById(
                    "feedbackMessage"
                );


            message.textContent =
                "Feedback recorded successfully. Database integration will be connected next.";


            feedbackForm.reset();

        }
    );

}



// ------------------------------------------
// Dashboard
// ------------------------------------------

function updateDashboard(results) {


    const highCount =
        document.getElementById("highCount");

    const mediumCount =
        document.getElementById("mediumCount");

    const lowCount =
        document.getElementById("lowCount");


    if (!highCount ||
        !mediumCount ||
        !lowCount) {

        return;
    }


    let high = 0;
    let medium = 0;
    let low = 0;


    results.forEach(function(item) {

        if (item.level === "HIGH") {

            high++;

        }
        else if (item.level === "MEDIUM") {

            medium++;

        }
        else {

            low++;

        }

    });


    highCount.textContent = high;
    mediumCount.textContent = medium;
    lowCount.textContent = low;

}