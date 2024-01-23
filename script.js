var initialKnobValues = {};


document.addEventListener("DOMContentLoaded", function() {
    var jsonData = '{"MasterVo": 0.699999988079071, "A Vol": 0.75, "A Pan": 0.5}'; // JSON string
    var data = JSON.parse(jsonData);

    var checkList = document.getElementById('list1');
    // Create "All" and "None" buttons
    var ul = checkList.querySelector('.items');

    // Create "All" and "None" buttons
    var allButton = document.createElement('button');
    allButton.textContent = 'All';
    var noneButton = document.createElement('button');
    noneButton.textContent = 'None';
    
    // Append buttons to the top of the list
    ul.insertBefore(allButton, ul.firstChild); // Insert 'All' button at the top
    ul.insertBefore(noneButton, ul.firstChild.nextSibling); // Insert 'None' button after 'All'
    

    checkList.getElementsByClassName('anchor')[0].onclick = function(evt) {
        if (checkList.classList.contains('visible'))
            checkList.classList.remove('visible');
        else
            checkList.classList.add('visible');
    };

    // Event listener for 'All' button
    allButton.addEventListener('click', function() {
        var checkboxes = ul.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(function(checkbox) {
            checkbox.checked = true;
            // Simulate the onchange event
            checkbox.onchange();
        });
    });

    // Event listener for 'None' button
    noneButton.addEventListener('click', function() {
        var checkboxes = ul.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(function(checkbox) {
            checkbox.checked = false;
            // Simulate the onchange event
            checkbox.onchange();
        });
    });


    // Create list items from JSON keys and attach event listeners
    var ul = checkList.querySelector('.items');
   // Object.keys(data).forEach(function(key) {
    Object.keys(data).forEach(function(key, index) { // Add 'index' as the second parameter
        var li = document.createElement('li');
        var checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.checked = true;
        checkbox.onchange = function() {
            var knobContainer = document.getElementById('knob-container-' + key);
            if (knobContainer) {
                knobContainer.style.display = this.checked ? '' : 'none';
            }
            var newJson = generateCheckedJson();
            console.log("Updated JSON:", newJson);
        };
        li.appendChild(checkbox);
        li.appendChild(document.createTextNode(' ' + key));
        ul.appendChild(li);
    });

    // Create a knob for each key in the JSON object
    Object.keys(data).forEach(function(key, index) {
        const knobContainer = createKnobContainer(key, data[key], index);
        document.body.appendChild(knobContainer);
        setupKnob(knobContainer, key, index, data[key]);
    });

    function formatValue(value) {
        if (value === 0) {
            return "0.0";
        } else if (value === 1) {
            return "1.0";
        } else {
            // Use toPrecision(17) to handle 16 decimal places
            return Number(value.toPrecision(17)).toString();
        }
    }

    function randomizeValue(value, minPercent, maxPercent) {
        // Randomize within the specified range
        let randomFactor = Math.random() * (maxPercent / 100.0 - minPercent / 100.0) + minPercent / 100.0;
        let newValue = value * randomFactor;
    
        // Add additional random decimal factor for precision
        let decimalFactor = Math.random() * (1 - randomFactor);
        let finalValue = newValue + decimalFactor;
    
        // Ensure the final value is within [0, 1] and has 16 decimal places
        return Math.min(Math.max(finalValue.toFixed(16), 0.0), 1.0);
    }
    
    
    document.getElementById("randomize-button").addEventListener("click", function() {
        let minPercent = document.getElementById("min-slider").value;
        let maxPercent = document.getElementById("max-slider").value;
        const minAngle = -126; // Define minAngle here
        const maxAngle = 126; // Define maxAngle here
        const rotationRange = maxAngle - minAngle;
    
        //Object.keys(data).forEach(function(key) {
        Object.keys(data).forEach(function(key, index) {
            let currentValue = parseFloat(data[key]);
            let randomizedValue = randomizeValue(currentValue, minPercent, maxPercent);
            data[key] = randomizedValue.toString(); // Update the data object
            console.log("INDEX Object keys: "+index);
            // Update knob position, display, and neon effect
            let knobContainer = document.getElementById('knob-container-' + key);
            if (knobContainer) {
                let knob = knobContainer.querySelector('.knob');
                let valueDisplay = knobContainer.querySelector('.knob-value');
                let neonRing = knobContainer.querySelector('.neon-ring');
                let angle = (randomizedValue * rotationRange) + minAngle;
                knob.style.transform = 'rotate(' + angle + 'deg)';
                valueDisplay.textContent = parseFloat(randomizedValue).toFixed(3);
            
                // Update neon effect
                updateNeonEffect((angle - minAngle) / rotationRange, neonRing, key, index); // Pass key here
            }
        });
    
        var newJson = generateCheckedJson();
        console.log("Updated JSON:", newJson);
    });

        
    function resetKnobs() {
        const minAngle = -126;
        const maxAngle = 126;
        const rotationRange = maxAngle - minAngle;
        Object.keys(initialKnobValues).forEach(function(key) {
            let initialData = initialKnobValues[key];
            let knobContainer = document.getElementById('knob-container-' + key);
            if (knobContainer) {
                let knob = knobContainer.querySelector('.knob');
                let valueDisplay = knobContainer.querySelector('.knob-value');
                let neonRing = knobContainer.querySelector('.neon-ring');
                let movablePlate = knobContainer.querySelector('.movable-plate');
    
                knob.style.transform = 'rotate(' + initialData.angle + 'deg)';
                valueDisplay.textContent = initialData.value.toFixed(3);
                updateNeonEffect((initialData.angle - minAngle) / rotationRange, neonRing, key, initialData.index);
                movablePlate.style.transform = 'rotate(' + ((initialData.angle - minAngle) / (maxAngle - minAngle)) * 360 + 'deg)';
                
                data[key] = initialData.value.toString();
            }
        });
    
        var newJson = generateCheckedJson();
        console.log("Reset to manual JSON:", newJson);
    }
    
    
    document.getElementById("reset-button").addEventListener("click", function() {
        resetKnobs();
    });

    function setupKnob(container, key, index, initialValue) {
        const knob = container.querySelector('.knob');
        const knobLabel = container.querySelector('.knob-label'); // Get the knob label element

        const neonRing = container.querySelector('.neon-ring'); // Adjust selector if necessary
        createNeonEffect(neonRing, key, index);
        console.log(knob); // Check if the knob element is correctly selected
        console.log(neonRing);
        if (!neonRing) {
            console.error('Neon ring element not found in container', container);
            return; // Exit the function if neon ring is not found
        }

        if (!knob) {
            console.error('Knob element not found in container', container);
            return; // Exit the function if knob is not found
        }

        console.log('Knob:', key);
        console.log('Neon Ring:', neonRing);
        const path = neonRing.querySelector('path');
        console.log('Path:', path);

        const movablePlate = container.querySelector('.movable-plate');
       // const neonRing = container.querySelector('.static-plate div:first-child');
        

        const numberContainer = container.querySelector('.static-plate div:last-child');
        const valueDisplay = container.querySelector('.knob-value');
        
        // Constants for knob behavior
        let isDragging = false;
        let startY = 0;
        //let currentAngle = -126; // Adjust based on value from JSON
        const minAngle = -126;
        const maxAngle = 126;
        const rotationRange = maxAngle - minAngle;
        const pixelRange = 200;

        // Set initial rotation for the knob
        // Convert initial value to an angle
        let currentAngle = initialValue * rotationRange + minAngle;
        knob.style.transform = 'rotate(' + currentAngle + 'deg)';


      //  updateNeonEffect((currentAngle - minAngle) / rotationRange, neonRing);
        updateNeonEffect((currentAngle - minAngle) / rotationRange, neonRing, key, index);

        if (movablePlate) {
            movablePlate.style.transform = 'rotate(' + ((currentAngle - minAngle) / (maxAngle - minAngle)) * 360 + 'deg)';
        }
        
        // Event listeners for the knob
        knob.addEventListener('mousedown', function(e) {
            isDragging = true;
            startY = e.clientY;
            e.preventDefault();
        });

        var checkList = document.getElementById('list1');
        var ul = checkList.querySelector('.items');
    

        document.addEventListener('mousemove', function(e) {
            if (isDragging) {
                const deltaY = startY - e.clientY;
                let angle = currentAngle + (deltaY / pixelRange) * rotationRange;
                angle = Math.max(minAngle, Math.min(angle, maxAngle));
                knob.style.transform = 'rotate(' + angle + 'deg)';

                // Calculate and format the value with precision
                let value = (angle - minAngle) / rotationRange;
                let formattedValue = formatValue(value);
                valueDisplay.textContent = value.toFixed(3); // Display with 3 decimal places
                data[knobLabel.textContent] = formattedValue; // Store the formatted string with trailing 16 zeros, max 1.0 and min 0.0 (formatValue function)
 
                if (angle !== currentAngle) {
                    initialKnobValues[key] = {
                        angle: angle,
                        value: parseFloat(data[knobLabel.textContent]),
                        index: index // Store the index as well
                    };
                
                    currentAngle = angle;
                    startY = e.clientY;
                }

                // Generate and log the updated JSON for checked items
                var newJson = generateCheckedJson();
                console.log("Updated JSON:", newJson);

                // Update neon effect and movable plate
                updateNeonEffect((angle - minAngle) / rotationRange, neonRing, key, index);

                movablePlate.style.transform = 'rotate(' + ((angle - minAngle) / (maxAngle - minAngle)) * 360 + 'deg)';

                if (angle !== currentAngle) {
                  //  console.log(knob, ((angle - minAngle) / rotationRange).toFixed(16));
                  //  console.log(knobLabel.textContent, ((angle - minAngle) / rotationRange).toFixed(16)); // Log the label text and value

                    currentAngle = angle;
                    startY = e.clientY;
                }
            }
        });

        document.addEventListener('mouseup', function() {
            isDragging = false;
        });

        // Create neon effect and number elements for each knob
       // createNeonEffect(neonRing, index);
        createNumbers(numberContainer);
    }

    function generateCheckedJson() {
        var checkedData = {};
        var checkboxes = document.querySelectorAll('.dropdown-check-list ul.items input[type="checkbox"]');
        checkboxes.forEach(function(checkbox) {
            if (checkbox.checked) {
                var key = checkbox.nextSibling.nodeValue.trim();
                checkedData[key] = data[key]; // Uses the formatted string
            }
        });
        return checkedData;
    }
    
    
    function createKnobContainer(key, value, index) {
        const knobContainer = document.createElement('div');
        knobContainer.className = 'knob-container';
        knobContainer.id = 'knob-container-' + key;
    
        // Create a div for displaying the value
        const valueDisplay = document.createElement('div');
        valueDisplay.className = 'knob-value';
        valueDisplay.id = 'knob-value-' + key;
        valueDisplay.textContent = value.toFixed(3); // Display the initial value
        knobContainer.appendChild(valueDisplay);
    
        // Create static-plate
        const staticPlate = document.createElement('div');
        staticPlate.className = 'static-plate';
        knobContainer.appendChild(staticPlate);
    
        // Create neon-ring and number div inside static-plate
        const neonRing = document.createElement('div');
        neonRing.className = 'neon-ring'; // Now correctly creating the element
        neonRing.id = 'neon-ring-' + key;
        staticPlate.appendChild(neonRing);
    
        const numberDiv = document.createElement('div');
        numberDiv.id = 'number-' + key;
        staticPlate.appendChild(numberDiv);
    
        // Create movable-plate
        const movablePlate = document.createElement('div');
        movablePlate.className = 'movable-plate';
        movablePlate.id = 'movable-plate-' + key;
        knobContainer.appendChild(movablePlate);
    
        // Create knob
        const knob = document.createElement('div');
        knob.className = 'knob';
        knob.id = 'knob-' + key;
        knobContainer.appendChild(knob);
    
        // Create label for the knob name
        const label = document.createElement('div');
        label.className = 'knob-label';
        label.textContent = key;
        knobContainer.appendChild(label);
    
        return knobContainer;
    }
    

    function createNeonEffect(neonRing, key, index) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        const padding = 20; // Additional space for the glow
        const svgSize = 150 + padding * 2;
        svg.setAttribute('width', svgSize.toString());
        svg.setAttribute('height', svgSize.toString());
        svg.setAttribute('viewBox', `0 0 ${svgSize} ${svgSize}`);

        const sanitizedKey = key.replace(/\s+/g, '_');
        // Define the filter for the glow effect
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const filter = document.createElementNS('http://www.w3.org/2000/svg', 'filter');
        filter.id = 'glow-effect-' + sanitizedKey;
        
    
        const feGaussianBlur = document.createElementNS('http://www.w3.org/2000/svg', 'feGaussianBlur');
        feGaussianBlur.setAttribute('stdDeviation', '4'); // Adjust for desired blur
        feGaussianBlur.setAttribute('result', 'coloredBlur');
    
        const feMerge = document.createElementNS('http://www.w3.org/2000/svg', 'feMerge');
        const feMergeNode1 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode');
        feMergeNode1.setAttribute('in', 'coloredBlur');
        const feMergeNode2 = document.createElementNS('http://www.w3.org/2000/svg', 'feMergeNode');
        feMergeNode2.setAttribute('in', 'SourceGraphic');
    
        feMerge.appendChild(feMergeNode1);
        feMerge.appendChild(feMergeNode2);
        filter.appendChild(feGaussianBlur);
        filter.appendChild(feMerge);
        defs.appendChild(filter);
        svg.appendChild(defs);
    
        // Circle element

        



        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
       //const circleX = circleY = pathX = pathY = 75 + padding;

        circle.setAttribute('cx', '75');
        circle.setAttribute('cy', '75');
        circle.setAttribute('r', '70');
        circle.setAttribute('stroke', 'reansparrent');
        circle.setAttribute('stroke-width', '10');
        circle.setAttribute('fill', 'none');
    
        // Path element
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', 'M75 5 A 70 70 0 1 1 74 5');
       // path.setAttribute('d', `M${pathX} ${pathY - 70} A 70 70 0 1 1 ${pathX - 1} ${pathY - 70}`);
        path.setAttribute('stroke', 'orange');
        path.setAttribute('stroke-width', '7');
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke-dasharray', '0 439.6');
        path.setAttribute('stroke-linecap', 'round');

        console.log('Created path element with ID: neonPath-' + key + '-' + index); // Debugging line
       
       // path.id = 'neonPath-' + key + '-' + index; // Set the ID of the path element
        path.id = 'neonPath-' + sanitizedKey + '-' + index;
        console.log('Creating neon effect for key:', key);
        // Apply the glow effect filter to the path
        path.setAttribute('filter', 'url(#glow-effect-' + sanitizedKey + ')');
    
        svg.appendChild(circle);
        svg.appendChild(path);
        neonRing.appendChild(svg);
    }
    
    

    function createNumbers(numberContainer) {
        for (let i = 0; i <= 10; i++) {
            const numberDiv = document.createElement('div');
            numberDiv.className = `number number-${i}`;
            numberDiv.textContent = i;
            numberContainer.appendChild(numberDiv);
        }
    }
    function updateNeonEffect(value, neonRing, key, index) {
        let totalLength = 439.6;
        let neonLength = totalLength * value;

        const sanitizedKey = key.replace(/\s+/g, '_');
        let path = neonRing.querySelector('#neonPath-' + sanitizedKey + '-' + index); // Use key instead of index
    
        if (path) {
            path.setAttribute('stroke-dasharray', `${neonLength} ${totalLength - neonLength}`);
        } else {
            console.log()
            console.log('DEBUG #neonPath-' + sanitizedKey + '-' + index);
            console.error('Path element not found in neon ring', neonRing);
        }
    }
       
});
