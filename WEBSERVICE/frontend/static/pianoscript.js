document.addEventListener('DOMContentLoaded', function() {
    const piano = document.getElementById('piano');
    const notes = generatePianoNotes();
    let selectedDuration = 500; // Default duration
    const currentNoteDisplay = document.querySelector('.currentNote');
    const durationButtons = document.querySelectorAll('.duration-button');
    let activeTimeouts = {};

    // Retrieve the unique identifier for the uploaded FXP file
    let uniqueId = window.localStorage.getItem('uniqueId');

    // Initialize duration buttons
    durationButtons.forEach(button => {
        button.addEventListener('click', function() {
            selectedDuration = parseInt(this.getAttribute('data-duration'));
            updateDurationButtons(this);
        });
    });

    function updateDurationButtons(activeButton) {
        // Remove 'active' class from all buttons
        durationButtons.forEach(button => button.classList.remove('active'));
        // Add 'active' class to the clicked button
        activeButton.classList.add('active');
    }

    // Highlight the default duration button on load
    highlightDefaultDurationButton();

    function highlightDefaultDurationButton() {
        // Find the button that matches the default duration
        const defaultButton = Array.from(durationButtons).find(button => parseInt(button.getAttribute('data-duration')) === selectedDuration);
        // If found, update duration buttons to reflect the default state
        if (defaultButton) {
            updateDurationButtons(defaultButton);
        }
    }

    notes.forEach(note => {
        const key = document.createElement('li');
        key.className = `${note.type} key`;
        key.dataset.note = note.midi;
        piano.appendChild(key);

        key.addEventListener('mousedown', function() {
            playNoteAction(note, this);
        });
    });

    function playNoteAction(note, keyElement) {
        // Clear any existing timeout for this key
        if (activeTimeouts[note.midi]) {
            clearTimeout(activeTimeouts[note.midi]);
            keyElement.classList.remove('active', 'active-gradual');
        }
    
        // Apply immediate visual feedback
        keyElement.classList.add('active');
        currentNoteDisplay.textContent = note.name; // Display the note name immediately

        // Play the note and apply gradual effect upon playback start
        playNote(note.midi, selectedDuration, () => {
            keyElement.classList.add('active-gradual');
        });

        // Schedule removal of active state and clear note display
        activeTimeouts[note.midi] = setTimeout(() => {
            keyElement.classList.remove('active', 'active-gradual');
            if (currentNoteDisplay.textContent === note.name) {
                currentNoteDisplay.textContent = ''; // Clear if it matches the played note
            }
        }, selectedDuration + 1100); // Adjust for load delay
    }
    

    // Function to play note (fetch audio and play)
    // accept duration and use the uniqueId
    function playNote(midi, duration, onPlayCallback) {
        uniqueId = window.localStorage.getItem('uniqueId');
        fetch(`/play?note=${midi}&duration=${duration}&unique_id=${uniqueId}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.blob();
            })
            .then(blob => {
                const audioURL = URL.createObjectURL(blob);
                const audio = new Audio(audioURL);
                audio.play().then(onPlayCallback).catch(e => console.error('Error playing audio:', e));
            })
            .catch(error => console.error('Error fetching or playing the note:', error));
    }

});


function generatePianoNotes() {
    const notes = [];
    for (let midi = 21; midi <= 108; midi++) {
        const name = getNoteName(midi);
        const type = name.includes('#') ? 'black' : 'white';
        notes.push({ midi, name, type });
    }
    return notes;
}

function getNoteName(midi) {
    const scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    const octave = Math.floor(midi / 12) - 1;
    const name = scale[(midi % 12)];
    return `${name}${octave}`;
}

