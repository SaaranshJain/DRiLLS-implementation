import subprocess
import os
import re


class ABC:
    def __init__(self, executable_path="~/abc/executable/abc"):
        if os.path.exists("./abc.history"):
            os.remove("./abc.history")

        self.session = subprocess.Popen(executable_path, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        self.first_stdout = False
        self.output_re = re.compile(r"^(abc\s\d\d+>\s)+(.+)$")
        self.stats_re = re.compile(r"^.+i/o\s+=\s+(\d+)/\s+(\d+)\s+lat\s+=\s+(\d+)\s+and\s+=\s+(\d+)\s+lev\s+=\s+(\d+)\s*$")
        self.verbose_rewrite_re = re.compile(r"^Rewriting\sstatistics:\sTotal\scuts\stries\s*=\s*(\d+).+\sBad\scuts\sfound\s*=\s*(\d+).+\sTotal\ssubgraphs\s*=\s*(\d+).+\sUsed\sNPN\sclasses\s*=\s*(\d+).+\sNodes\sconsidered\s*=\s*(\d+).+\sNodes\srewritten\s*=\s*(\d+).+\sGain\s*=\s*(\d+).+\(\s+(\d+\.\d+)\s*\%\)(.+\s)+TOTAL\s*=\s*(\d+\.\d+).+$")

    def _readline(self):
        return self.session.stdout.readline().decode("utf-8").strip()

    def _writeline(self, message: str):
        self.session.stdin.write(f"{message.strip()}\n".encode("utf-8"))
        self.session.stdin.flush()

    def read_aiger(self, aig_path: str):
        self._writeline(f"read {aig_path}")

    def print_stats(self):
        self._writeline("print_stats")

        if not self.first_stdout:
            self.first_stdout = True
            self._readline()
            self._readline()
            self._readline()

        txt = self.output_re.match(self._readline()).group(2)
        matches = self.stats_re.match(txt)
        num_inputs = int(matches.group(1))
        num_outputs = int(matches.group(2))
        num_latches = int(matches.group(3))
        num_ands = int(matches.group(4))
        num_levels = int(matches.group(5))

        self._writeline("write temp.aig")
        output = subprocess.run(["./get_stats", "temp.aig"], capture_output=True, text=True)
        os.remove("temp.aig")
        total_nodes, total_edges, not_gates = map(int, output.stdout.strip().split())

        return [num_inputs, num_outputs, total_nodes, total_edges, num_levels, num_latches, num_ands, not_gates]
    
    def balance(self):
        self._writeline("balance")

    def rewrite(self, preserve_levels=True, zero_cost=False, verbose=False):
        command = " -" if (not preserve_levels) or zero_cost or verbose else ""

        if not preserve_levels:
            command += "l"
        if zero_cost:
            command += "z"
        if verbose:
            command += "v"

        self._writeline(f"rewrite{command}")
        if not verbose:
            return
        
        if not self.first_stdout:
            self.first_stdout = True
            self._readline()
            self._readline()
            self._readline()

        txt = self.output_re.match(self._readline()).group(2)
        matches = self.verbose_rewrite_re.match(txt)
        total_cuts_tries = int(matches.group(1))
        bad_cuts_found = int(matches.group(2))
        total_subgraphs = int(matches.group(3))
        used_npn_classes = int(matches.group(4))
        nodes_considered = int(matches.group(5))
        nodes_rewritten = int(matches.group(6))
        gain = int(matches.group(7))
        percentage_gain = float(matches.group(8))
        total_time_taken = float(matches.group(9))
        return [total_cuts_tries, bad_cuts_found, total_subgraphs, used_npn_classes, nodes_considered, nodes_rewritten, gain, percentage_gain, total_time_taken]

    def cec(self):
        self._writeline("cec")

        if not self.first_stdout:
            self.first_stdout = True
            self._readline()
            self._readline()
            self._readline()

        txt = self.output_re.match(self._readline()).group(2)
        return txt

    def quit(self):
        self._writeline("quit")
        self.session.stdin.close()
        self.session.terminate()
        return self.session.wait(timeout=1)
