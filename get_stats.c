#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// Function to read delta-encoded integers
int read_delta(FILE *f) {
    int result = 0;
    int shift = 0;
    unsigned char byte;
    while (1) {
        if (fread(&byte, 1, 1, f) != 1) {
            break; // End of file or error
        }
        result |= (byte & 0x7F) << shift;
        if ((byte & 0x80) == 0) {
            break;
        }
        shift += 7;
    }
    return result;
}

// Function to parse binary AIGER files
void parse_binary_aiger(const char *file_path) {
    FILE *f = fopen(file_path, "rb");
    if (!f) {
        perror("Error opening file");
        return;
    }

    // Read the header
    char header[128];
    if (!fgets(header, sizeof(header), f)) {
        perror("Error reading header");
        fclose(f);
        return;
    }

    int M, I, L, O, A;
    if (sscanf(header, "aig %d %d %d %d %d", &M, &I, &L, &O, &A) != 5) {
        fprintf(stderr, "Error parsing header\n");
        fclose(f);
        return;
    }

    // Initialize counters
    int not_gates = 0;

    // Skip inputs (I literals)
    for (int i = 0; i < I; i++) {
        uint32_t input;
        fread(&input, sizeof(uint32_t), 1, f);
    }

    // Skip latches (L pairs)
    for (int i = 0; i < L; i++) {
        uint64_t latch;
        fread(&latch, sizeof(uint64_t), 1, f);
    }

    // Count edges for outputs
    for (int i = 0; i < O; i++) {
        uint32_t lit;
        fread(&lit, sizeof(uint32_t), 1, f);
        
        if (lit % 2 == 1) { // Check if complemented
            not_gates++;
        }
    }

    // Decode AND gates using delta encoding
    int last_lhs = 0, last_rhs0 = 0, last_rhs1 = 0;
    for (int i = 0; i < A; i++) {
        int delta_lhs = read_delta(f);
        int delta_rhs0 = read_delta(f);
        int delta_rhs1 = read_delta(f);

        int lhs = last_lhs + delta_lhs;
        int rhs0 = last_rhs0 + delta_rhs0;
        int rhs1 = last_rhs1 + delta_rhs1;

        last_lhs = lhs;
        last_rhs0 = rhs0;
        last_rhs1 = rhs1;

        // Check for complemented edges
        if (rhs0 % 2 == 1) {
            not_gates++;
        }
        if (rhs1 % 2 == 1) {
            not_gates++;
        }
    }

    printf("%d\n", not_gates);
    fclose(f);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <file_path>\n", argv[0]);
        return 1;
    }

    parse_binary_aiger(argv[1]);

    return 0;
}
