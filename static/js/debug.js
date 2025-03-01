// Debug script for Netlify deployment
document.addEventListener('DOMContentLoaded', function() {
    console.log('Debug script loaded');
    
    // Create debug info element
    const debugInfo = document.createElement('div');
    debugInfo.style.position = 'fixed';
    debugInfo.style.bottom = '10px';
    debugInfo.style.right = '10px';
    debugInfo.style.backgroundColor = 'rgba(0,0,0,0.7)';
    debugInfo.style.color = 'white';
    debugInfo.style.padding = '10px';
    debugInfo.style.borderRadius = '5px';
    debugInfo.style.fontSize = '12px';
    debugInfo.style.zIndex = '9999';
    debugInfo.style.maxWidth = '300px';
    debugInfo.style.maxHeight = '200px';
    debugInfo.style.overflow = 'auto';
    
    // Add debug info
    const info = [
        `URL: ${window.location.href}`,
        `CSS loaded: ${Array.from(document.styleSheets).map(s => s.href).filter(Boolean).join(', ') || 'None external'}`,
        `Scripts loaded: ${Array.from(document.scripts).map(s => s.src).filter(Boolean).join(', ') || 'None external'}`,
        `Window size: ${window.innerWidth}x${window.innerHeight}`,
        `User Agent: ${navigator.userAgent}`
    ];
    
    debugInfo.innerHTML = info.join('<br>');
    document.body.appendChild(debugInfo);
    
    // Add toggle button
    const toggleButton = document.createElement('button');
    toggleButton.textContent = 'Toggle Debug';
    toggleButton.style.position = 'fixed';
    toggleButton.style.bottom = '10px';
    toggleButton.style.right = '10px';
    toggleButton.style.zIndex = '10000';
    toggleButton.style.padding = '5px';
    toggleButton.style.backgroundColor = '#2A93D5';
    toggleButton.style.color = 'white';
    toggleButton.style.border = 'none';
    toggleButton.style.borderRadius = '3px';
    toggleButton.style.cursor = 'pointer';
    
    toggleButton.addEventListener('click', function() {
        if (debugInfo.style.display === 'none') {
            debugInfo.style.display = 'block';
            toggleButton.style.bottom = `${debugInfo.offsetHeight + 20}px`;
        } else {
            debugInfo.style.display = 'none';
            toggleButton.style.bottom = '10px';
        }
    });
    
    document.body.appendChild(toggleButton);
    debugInfo.style.display = 'none';
}); 