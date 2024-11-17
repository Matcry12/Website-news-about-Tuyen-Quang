function submitSortForm(checkbox) {
    // Uncheck the other checkbox when one is selected
    document.querySelectorAll('input[name="priceSort"]').forEach((cb) => {
        if (cb !== checkbox) cb.checked = false;
    });

    // Submit the form after updating checkboxes
    document.getElementById('sortForm').submit();
}