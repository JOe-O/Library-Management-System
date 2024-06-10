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
            if (response.status === 200) {
                return response.json();
            } else if (response.status === 400) {
                return response.json().then(data => {
                    throw new Error(data.message);
                });
            } else {
                throw new Error('Failed to borrow book');
            }
        })
        .then(data => {
            alert(data.message);
            loadContent('books'); // Reload the books page after borrowing
        })
        .catch(error => {
            alert(error.message); // Display the error message
            console.error('Error borrowing book:', error);
        });
}


// function borrowBook(bookId) {
//     fetch('/borrow/' + bookId, { method: 'POST' })
//         .then(response => {
//             if (!response.ok) {
//                 alert('bad request')
//                 throw new Error('Failed to borrow book');
//             }
//             return response.json();
//         })
//         .then(data => {
//             if (data.message === 'The book is not available for borrowing') {
//                 alert(data.message);
//             } else {
//                 alert('Book borrowed successfully');
//                 loadContent('books'); // Reload the books page after borrowing
//             }
//         })
//         .catch(error => console.error('Error borrowing book:', error));
// }