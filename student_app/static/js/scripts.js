// Example: Alert when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log("Student profile page loaded successfully!");
});

// Example: Toggle back button highlight
const backBtn = document.querySelector('.back-btn');
if(backBtn){
    backBtn.addEventListener('mouseover', () => {
        backBtn.style.color = '#004080';
    });
    backBtn.addEventListener('mouseout', () => {
        backBtn.style.color = '';
    });
}

