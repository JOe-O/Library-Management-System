function loadContent(page) {
    fetch('/' + page)
        .then(response => response.text())
        .then(data => {
            document.getElementById('main-content').innerHTML = data;
        })
        .catch(error => console.error('Error loading content:', error));
}

function editBook(bookId) {
    loadContent('edit_book/' + bookId);
}

function addBook() {
    loadContent('add_book');
}
function changePassword(userId) {

    loadContent('change_password/' + userId);
}

function changeRole(userId) {

    loadContent('change_role/' + userId);
}

function addUser() {
    
    loadContent('add_user');
}


function borrowBook(bookId) {
    fetch('/borrow/' + bookId, { method: 'POST' })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to borrow book');
            }
            return response.text();
        })
        .then(data => {
            alert(data);
            loadContent('books'); // Reload the books page after borrowing
        })
        .catch(error => console.error('Error borrowing book:', error));
}