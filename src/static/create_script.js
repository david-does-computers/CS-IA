document.getElementById('category_id').addEventListener('change', function () {
    var newCategory = document.getElementById('new_category');
    if (this.value == '-1') {
      newCategory.style.display = 'block';
      newCategory.required = true;
      this.style.gridColumn = "span 1";
      console.log("full");
      
      
    } else {
      newCategory.style.display = 'none';
      newCategory.required = false;
      this.style.gridColumn = "span 2";
    }
  });