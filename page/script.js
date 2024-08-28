document.getElementById('csvFileInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const csv = e.target.result;
        const lines = csv.split('\n');
        const tableHeaders = document.getElementById('tableHeaders');
        const csvList = document.getElementById('csvList');
        
        // Leeren der Tabelle
        tableHeaders.innerHTML = '';
        csvList.innerHTML = '';

        // Spaltenbezeichnungen
        const headers = ['Name', 'Klasse', 'Level', 'Bosskiller', 'Bevorzugter Boss'];
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            tableHeaders.appendChild(th);
        });

        // Restliche Zeilen als Listeneinträge
        lines.slice(1).forEach((line, index) => {
            const columns = line.split(',');
            if (columns.length === headers.length) { // Prüfen, ob die Zeile gültige Daten enthält
                const tr = document.createElement('tr');
                tr.id = `row-${index}`;
                tr.draggable = true;
                tr.ondragstart = drag;
                columns.forEach((column, colIndex) => {
                    const td = document.createElement('td');

                    // Check for "Bosskiller" column and replace "Ja" with a skull emoji, leave "Nein" empty
                    if (headers[colIndex] === 'Bosskiller') {
                        if (column.trim().toLowerCase() === 'ja') {
                            td.textContent = '💀'; // Totenkopf-Symbol
                        } else {
                            td.textContent = ''; // Leer lassen, wenn "Nein"
                        }
                    } else {
                        td.textContent = column.trim();
                    }

                    tr.appendChild(td);
                });
                csvList.appendChild(tr);
            }
        });
    };

    reader.readAsText(file);
});

function allowDrop(event) {
    event.preventDefault();
}

function drag(event) {
    event.dataTransfer.setData("text", event.target.id);
}

function drop(event) {
    event.preventDefault();
    const data = event.dataTransfer.getData("text");
    const row = document.getElementById(data);

    if (row) {
        const dropTarget = event.target.closest('.gruppe-content, #csvList');

        if (dropTarget && dropTarget.id === 'csvList') {
            // Zeile in die Teilnehmerliste zurück verschieben
            const originalGroup = row.closest('.gruppe');
            if (originalGroup) {
                const originalTable = originalGroup.querySelector('table');
                if (originalTable) {
                    originalTable.removeChild(row);

                    // Überprüfe, ob Gruppe leer ist und neutralisiert werden soll
                    const rowCount = originalTable.querySelectorAll('tr').length;
                    if (rowCount === 0) {
                        originalTable.remove();
                    }
                    if (rowCount < 4) {
                        const vollText = originalGroup.querySelector('.gruppe-voll');
                        if (vollText) {
                            vollText.remove();
                        }
                    }
                    updateGroupColor(originalGroup); // Farbe der Gruppe und Totenkopf-Emoji aktualisieren
                }
            }
            removeRemoveButton(row); // Entferne den Button, bevor die Zeile in die Teilnehmerliste zurückgeht
            dropTarget.appendChild(row);
        } else if (dropTarget && dropTarget.classList.contains('gruppe-content')) {
            // Prüfen, ob die Gruppe voll ist
            const table = dropTarget.querySelector('table');
            const rowCount = table ? table.querySelectorAll('tr').length : 0;

            if (rowCount < 4) {
                // Füge die Zeile in die Gruppe ein
                if (!table) {
                    const newTable = document.createElement('table');
                    newTable.appendChild(row);
                    dropTarget.appendChild(newTable);
                } else {
                    table.appendChild(row);
                }

                addRemoveButton(row); // Füge den Entfernen-Button hinzu
                updateGroupColor(dropTarget.closest('.gruppe')); // Farbe der Gruppe und Totenkopf-Emoji aktualisieren

                // Falls die Gruppe nach dem Hinzufügen voll ist, "Gruppe voll" anzeigen
                if (rowCount === 3) {
                    const headerDiv = dropTarget.closest('.gruppe').querySelector('.gruppe-header');
                    if (!headerDiv.querySelector('.gruppe-voll')) {
                        const vollText = document.createElement('span');
                        vollText.textContent = ' (Gruppe voll)';
                        vollText.className = 'gruppe-voll';
                        vollText.style.fontStyle = 'italic';
                        vollText.style.fontSize = 'smaller';
                        headerDiv.appendChild(vollText);
                    }
                }
            } else {
                alert("Diese Gruppe ist voll. Du kannst keine weiteren Einträge hinzufügen.");
            }
        }
    }
}

function addRemoveButton(row) {
    const removeButton = document.createElement('button');
    removeButton.textContent = '-';
    removeButton.style.marginLeft = '10px';
    removeButton.onclick = function () {
        const csvList = document.getElementById('csvList');
        const table = row.closest('table');
        const group = row.closest('.gruppe');

        table.removeChild(row);
        removeRemoveButton(row); // Entferne den Button, bevor die Zeile zurückgeht
        csvList.appendChild(row);

        // Überprüfen, ob die Gruppe leer ist und neutralisiert werden soll
        const rowCount = table.querySelectorAll('tr').length;
        if (rowCount === 0) {
            table.remove();
        }
        if (rowCount < 4) {
            const vollText = group.querySelector('.gruppe-voll');
            if (vollText) {
                vollText.remove();
            }
        }
        updateGroupColor(group); // Farbe der Gruppe und Totenkopf-Emoji aktualisieren
    };

    const td = document.createElement('td');
    td.appendChild(removeButton);
    row.appendChild(td);
}

function removeRemoveButton(row) {
    const lastTd = row.querySelector('td:last-child');
    if (lastTd && lastTd.querySelector('button')) {
        lastTd.remove();
    }
}

function updateGroupColor(group) {
    const table = group.querySelector('table');
    if (!table) {
        group.style.backgroundColor = ''; // Standardfarbe, wenn keine Zeilen vorhanden sind
        removeSkullEmoji(group);
        return;
    }

    const hasBosskiller = Array.from(table.querySelectorAll('td')).some(td => td.textContent === '💀');

    if (hasBosskiller) {
        group.style.backgroundColor = '#d4edda'; // Leichtes Grün
        addSkullEmoji(group, false); // Totenkopf-Emoji hinzufügen, normal
    } else {
        group.style.backgroundColor = '#fff3cd'; // Leichtes Orange
        addSkullEmoji(group, true); // Totenkopf-Emoji hinzufügen, durchgestrichen
    }
}

function addSkullEmoji(group, crossedOut) {
    let skull = group.querySelector('.skull-emoji');
    if (!skull) {
        skull = document.createElement('span');
        skull.className = 'skull-emoji';
        skull.style.fontSize = '2em';
        skull.style.position = 'absolute';
        skull.style.top = '10px';
        skull.style.right = '10px';
        group.style.position = 'relative'; // Damit das Emoji relativ zur Gruppe positioniert wird
        group.appendChild(skull);
    }
    skull.textContent = crossedOut ? '💀❌' : '💀';
}

function removeSkullEmoji(group) {
    const skull = group.querySelector('.skull-emoji');
    if (skull) {
        skull.remove();
    }
}

document.getElementById('addParticipantBtn').addEventListener('click', function() {
    const name = document.getElementById('nameInput').value.trim();
    const charClass = document.getElementById('classInput').value.trim();
    const level = document.getElementById('levelInput').value.trim();
    const bosskiller = document.getElementById('bosskillerInput').value.trim();
    const favoriteBoss = document.getElementById('favoriteBossInput').value.trim();

    if (name && charClass && level) {
        addParticipantToList(name, charClass, level, bosskiller, favoriteBoss);
        clearFormInputs();
    } else {
        alert("Bitte füllen Sie die Felder Name, Klasse und Level aus.");
    }
});

function addParticipantToList(name, charClass, level, bosskiller, favoriteBoss) {
    const csvList = document.getElementById('csvList');

    const tr = document.createElement('tr');
    tr.draggable = true;
    tr.ondragstart = drag;

    const nameTd = document.createElement('td');
    nameTd.textContent = name;
    tr.appendChild(nameTd);

    const classTd = document.createElement('td');
    classTd.textContent = charClass;
    tr.appendChild(classTd);

    const levelTd = document.createElement('td');
    levelTd.textContent = level;
    tr.appendChild(levelTd);

    const bosskillerTd = document.createElement('td');
    if (bosskiller === 'Ja') {
        bosskillerTd.textContent = '💀'; // Totenkopf-Symbol
    } else {
        bosskillerTd.textContent = ''; // Leer lassen, wenn "Nein"
    }
    tr.appendChild(bosskillerTd);

    const favoriteBossTd = document.createElement('td');
    favoriteBossTd.textContent = favoriteBoss;
    tr.appendChild(favoriteBossTd);

    // Füge eine eindeutige ID zur Zeile hinzu, damit Drag-and-Drop funktioniert
    const rowId = `row-${csvList.getElementsByTagName('tr').length}`;
    tr.id = rowId;

    csvList.appendChild(tr);
}

function clearFormInputs() {
    document.getElementById('nameInput').value = '';
    document.getElementById('classInput').value = '';
    document.getElementById('levelInput').value = '';
    document.getElementById('bosskillerInput').value = '';
    document.getElementById('favoriteBossInput').value = '';
}
