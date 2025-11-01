

    $.validator.addMethod("alphanumericOrNumerical", function(value, element) {
        // Regex to allow all alphanumeric characters, whitespace, and special characters including ~ and `
        var regex = /^(?:(?!\s{2})[a-zA-Z0-9\s!@#$%^&*()_+=\-[\]{};':"\\|,.<>\/?~`])+$/;
        // Ensure there is at least one letter and no double spaces
        return this.optional(element) || regex.test(value)
            && !(/^[\d\s!@#$%^&*()_+=\-[\]{};':"\\|,.<>\/?~`]+$/.test(value))
            && /[a-zA-Z]/.test(value);
    }, "Please enter at least one alphabetic character (double spaces are not allowed).");
    $.validator.addMethod("noDoubleSpaces", function(value, element) {
        return this.optional(element) || !/\s{2,}/.test(value);
}, "Double spaces are not allowed.");
    $.validator.addMethod("notEqual", function(value, element, param) {
    return this.optional(element) || value !== $(param).val();
    }, "Mobile number and Alternate number must not be the same.");

    $.validator.addMethod("passwordPattern", function (value, element) {
        return /^(?=.*[A-Z])(?=.*\d)(?=.*[#@$!%*?&])[A-Za-z\d#@$!%*?&]{6,16}$/.test(value);
    }, "Password must contain at least 1 uppercase letter, 1 number, and 1 special character");

    $.validator.addMethod("phone_no", function (value, element) {

        return this.optional(element) || /^[0-9]{6,}$/.test(value);
    }, "Password must contain at least 1 uppercase letter, 1 number, and 1 special character");

    $.validator.addMethod("fullname_valid", function (value, element) {
        return this.optional(element) || /^(?!.* {2})[A-Za-z, ]+$/.test(value);
    }, "Full Name can only contain alphabets, commas, and single spaces between words.");

    $.validator.addMethod("phoneOrEmail", function (value, element) {
        let phoneRegex = /^[6-9]\d{9}$/; // Validates a 10-digit phone number starting with 6-9
        let emailRegex =
        /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/; // Standard email format
        return phoneRegex.test(value) || emailRegex.test(value);
    }, "Enter a valid Email, Phone (10-digit) or CRN");
    // Phone number validation (10 digits, starts with 6-9)
    $.validator.addMethod("phoneNumber", function (value, element) {
        let phoneRegex = /^[6-9]\d{9}$/;
        return this.optional(element) || phoneRegex.test(value);
    }, "Please enter a valid 10-digit phone number starting with 6-9.");

    // Email validation (standard format)
    $.validator.addMethod("emailAddress", function (value, element) {
        let emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return this.optional(element) || emailRegex.test(value);
    }, "Please enter a valid email address.");

    $.validator.addMethod("aadharNumber", function (value, element) {
        return this.optional(element) || /^\d{12}$/.test(value);
    }, "Aadhar Number must be exactly 12 digits without spaces");

    // PAN Number Validation (5 letters + 4 digits + 1 letter)
    $.validator.addMethod("panNumber", function (value, element) {
        return /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(value);
    }, "PAN Number must be in the format: AAAAA9999A");

    $.validator.addMethod("fileExtension", function (value, element) {
        if (this.optional(element)) return true;
        var file = element.files[0];
        if (file) {
            var ext = file.name.split('.').pop().toLowerCase();
            return ext === "png" || ext === "jpg";
        }
        return false;
    }, "Only PNG and JPG files are allowed");
    $.validator.addMethod("fileExtensions", function (value, element) {
        if (this.optional(element)) return true;
        var file = element.files[0];
        if (file) {
            var ext = file.name.split('.').pop().toLowerCase();
            return ext === "png" || ext === "jpg" || ext === "jpeg";
        }
        return false;
    }, "Only PNG, JPG, and JPEG files are allowed");

   $.validator.addMethod("fileExtensionpdf", function (value, element) {
        if (this.optional(element)) return true;
        var file = element.files[0];
        if (file) {
            var ext = file.name.split('.').pop().toLowerCase();
            return ext === "pdf";
        }
        return false;
    }, "Only PDF file is allowed");




document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const form = document.getElementById('upload-form');
    const previewContainer = document.getElementById('filePreview');


    dropZone.addEventListener('click', () => fileInput.click());


    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    // Drop handler
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {

        if (!file.name.toLowerCase().endsWith('.csv')) {
            alert('Only CSV files are allowed!');
            return;
        }

        previewContainer.innerHTML = '';


        const preview = document.createElement('div');
        preview.className = 'preview-item';
        preview.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="flex-shrink-0 me-3">
                    <div class="avatar-sm bg-light rounded">
                        <img src="static/admin_assets/images/brands/new-document.png"
                                class="img-fluid rounded"
                                alt="File icon">
                    </div>
                </div>
                <div class="flex-grow-1">
                    <h5 class="fs-14 mb-1">${file.name}</h5>
                    <p class="fs-13 text-muted mb-0">
                        ${(file.size / 1024).toFixed(2)} KB
                    </p>
                </div>
                <div class="flex-shrink-0 ms-3">
                    <button type="button" class="btn btn-sm btn-danger"
                            onclick="clearFile()">
                        Remove
                    </button>
                </div>
            </div>
        `;

        previewContainer.appendChild(preview);
    }


    form.addEventListener('submit', function (e) {
        if (!fileInput.files.length) {
            e.preventDefault();
            alert('Please select a CSV file first!');
        }
    });
});


function clearFile() {
    document.getElementById('fileInput').value = '';
    document.getElementById('filePreview').innerHTML = '';
}

