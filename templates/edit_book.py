{% extends "base.html" %}

{% block page_title %}Edit Book{% endblock %}

{% block content %}
<div class="form-container">
    <h5><i class="bi bi-pencil"></i> Edit Book</h5>
    <hr>
    
    <form method="POST">
        <div class="mb-3">
            <label class="form-label">Book Title</label>
            <input type="text" name="title" class="form-control" value="{{ book.title }}" required>
        </div>
        
        <div class="mb-3">
            <label class="form-label">Author</label>
            <input type="text" name="author" class="form-control" value="{{ book.author }}" required>
        </div>
        
        <div class="mb-3">
            <label class="form-label">Quantity</label>
            <input type="number" name="quantity" class="form-control" value="{{ book.quantity }}" min="0" required>
        </div>
        
        <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary flex-grow-1">
                <i class="bi bi-check-circle"></i> Update Book
            </button>
            <a href="{{ url_for('books') }}" class="btn btn-secondary">
                <i class="bi bi-x-circle"></i> Cancel
            </a>
        </div>
    </form>
</div>
{% endblock %}