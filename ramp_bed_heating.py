import re
import sys
import urllib.request
import json

# ==========================================================
# CONFIGURAZIONE: Inserisci qui l'IP e la porta del tuo KX-Bridge
# ==========================================================
BRIDGE_BASE_URL = "http://192.168.xxx.xxx:7125" 

def get_current_bed_temp():
    url = f"{BRIDGE_BASE_URL}/api/state"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'OrcaSlicer/1.0'})
        with urllib.request.urlopen(req, timeout=2) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # Controllo diretto e secco come richiesto. Niente fallback nidificati.
            if 'bed_temp' in data:
                return float(data['bed_temp'])
                
    except Exception:
        pass # Se il bridge non risponde, usa il default
    return 20.0

def process_gcode(file_path):
    start_temp = get_current_bed_temp()
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 1. Cerca il passo in gradi (default 10°C se non specificato)
    step_deg = 10
    for line in lines:
        match = re.search(r';\s*RAMP_STEP\s*=\s*(\d+)', line)
        if match:
            step_deg = int(match.group(1))
            break
            
    # 2. Cerca la riga G9111 e le sue temperature
    g9111_idx = -1
    bed_target = None
    
    for i, line in enumerate(lines):
        g9111_match = re.search(r'^\s*G9111\s+(.*)', line)
        if g9111_match:
            g9111_idx = i
            params = g9111_match.group(1)
            
            bed_match = re.search(r'bedTemp=(\d+\.?\d*)', params)
            if bed_match:
                val = float(bed_match.group(1))
                if val > 0: bed_target = val
            break # Trovato G9111, usciamo
            
    # Fallback: se non c'è G9111, cerca M140/M190 standard (Piano B)
    if g9111_idx == -1:
        for i, line in enumerate(lines):
            match = re.search(r'^\s*M1[49]0\s+S(\d+\.?\d*)', line)
            if match:
                val = float(match.group(1))
                if val > 0:
                    bed_target = val
                    g9111_idx = i # Usiamo questo indice come punto di iniezione
                    break

    # Se non c'è riscaldamento del piatto, esci lasciando il file intatto
    if bed_target is None:
        return
        
    bed_target_int = int(round(bed_target))
    
    # 3. Calcola i gradini dinamici
    steps = []
    if step_deg == 0:
        steps.append(bed_target_int)
    else:
        current = start_temp
        while current < bed_target_int - 1:
            next_step = current + step_deg
            if next_step >= bed_target_int:
                steps.append(bed_target_int)
                break
            else:
                steps.append(int(round(next_step)))
                current = next_step
        if not steps:
            steps.append(bed_target_int)
            
    # 4. Costruisci la rampa da iniettare
    ramp_commands = [f"; === Pre-Rampa Dinamica (target: {bed_target_int}°C, start: {start_temp}°C, step: {step_deg}°C) ===\n"]
    
    for i, step_temp in enumerate(steps):
        if step_temp > start_temp:
            ramp_commands.append(f"M190 S{step_temp} ; Step {i+1}: {step_temp}°C\n")
        else:
            ramp_commands.append(f"; Step {i+1} saltato: {step_temp}°C <= {start_temp}°C (già caldo)\n")
            
    ramp_commands.append(f"; === Fine Pre-Rampa (prosegue con G9111) ===\n")
    
    # 5. LOGICA DI SPOSTAMENTO COMMENTO
    comment_to_move = None
    cut_idx = g9111_idx 

    # Controlla se la riga prima di G9111 è il commento "Avvio Macro..."
    if g9111_idx > 0 and "Avvio Macro originale Anycubic" in lines[g9111_idx - 1]:
        comment_to_move = lines[g9111_idx - 1]
        cut_idx = g9111_idx - 1 
        
        # Se c'è una riga vuota prima del commento, tagliamo via anche quella
        if g9111_idx > 1 and lines[g9111_idx - 2].strip() == "":
            cut_idx = g9111_idx - 2

    # Costruiamo il blocco finale da iniettare
    block_to_inject = list(ramp_commands)
    
    if comment_to_move:
        block_to_inject.append("\n")
        block_to_inject.append(comment_to_move)

    # 6. Inietta i comandi e sovrascrivi il file
    new_lines = lines[:cut_idx] + block_to_inject + lines[g9111_idx:]
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(1)
    process_gcode(sys.argv[1])