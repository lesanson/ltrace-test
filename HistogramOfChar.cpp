#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cctype>
#include <unordered_map>
#include <algorithm>

void readFilesAndCollectChars(const std::vector<std::string>& file_paths) {
    for (const auto& file_path : file_paths) {
        std::ifstream file(file_path);
        std::unordered_map<char, int> letterCount; // map to store frequencies

        std::cout << "Processing file: " << file_path << "\n";

        if (!file.is_open()) {
            std::cerr << "Unable to open file: " << file_path << "\n";
            continue;
        }

        std::string line;

        while (std::getline(file, line)) {
            for (char c : line) {
                if (std::isalpha(static_cast<unsigned char>(c))) {
                    // convert to lowercase and increment count in the map
                    char lowercaseChar = std::tolower(static_cast<unsigned char>(c));
                    letterCount[lowercaseChar]++;
                }
            }
        }

        file.close();

        // from map to vector
        std::vector<std::pair<char, int>> freqVector(letterCount.begin(), letterCount.end());

        // sort vector
        std::sort(freqVector.begin(), freqVector.end(),
            [](const std::pair<char, int>& a, const std::pair<char, int>& b) {
                return a.second > b.second;
            });

        // Print the letter frequencies
        std::cout << "Letter frequencies in descending order for " << file_path << ":\n";
        for (const auto& p : freqVector) {
            std::cout << p.first << ": " << p.second << "\n";
        }

        std::cout << "\n";
    }
}

int main() {
    std::vector<std::string> file_paths = {
        "YOUR_FILE_PATH_HERE.txt",
    };

    readFilesAndCollectChars(file_paths);

    return 0;
}

