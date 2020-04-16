 var deleteButtons = document.querySelectorAll('.delete');

// find all the delete buttons
deleteButtons.forEach(function(button){

    // Add event listner to all buttons
    button.addEventListener('click', function(ev){
        var okToDelete = confirm("Delete place - are you sure?");

        // If user presses no, prevent the form submit
        if (!okToDelete) {
            ev.preventDefault(); //Prevent the click event propagating
        }
    })
});
