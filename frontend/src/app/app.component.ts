import { Component } from '@angular/core';
import { DocumentService, AnalysisResult } from './document.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  selectedFiles: File[] = [];
  isDragging = false;
  analyzing = false;
  result: AnalysisResult | null = null;

  // For batch processing status
  currentProcessingFile = '';
  processedCount = 0;
  isCancelled = false;
  analyzingSummary = false;

  MAX_DOCS = 5;

  question = '';
  asking = false;
  answer = '';

  selectedTone = 'executive';
  tones = [
    { value: 'executive', label: 'Executive Summary (Brief)' },
    { value: 'detailed', label: 'Detailed Analysis' },
    { value: 'simplified', label: 'Simplified (ELi5)' }
  ];

  constructor(
    private documentService: DocumentService,
    private snackBar: MatSnackBar
  ) { }

  public handleDragOver(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = true;
  }

  public handleDragLeave(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;
  }

  public handleDrop(event: DragEvent) {
    event.preventDefault();
    event.stopPropagation();
    this.isDragging = false;

    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      this.handleFiles(event.dataTransfer.files);
    }
  }

  onFileSelected(event: any) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      this.handleFiles(target.files);
    }
  }

  private handleFiles(fileList: FileList | File[]) {
    const files = Array.from(fileList);

    if (this.selectedFiles.length + files.length > this.MAX_DOCS) {
      this.snackBar.open(`Maximum ${this.MAX_DOCS} files allowed. Some files were ignored.`, 'Close', { duration: 5000 });
    }

    for (const file of files) {
      if (this.selectedFiles.length >= this.MAX_DOCS) break;

      if (this.checkFile(file)) {
        // Prevent duplicates
        if (!this.selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
          this.selectedFiles.push(file);
        }
      }
    }
    this.result = null;
    this.answer = '';
  }

  removeFile(index: number) {
    this.selectedFiles.splice(index, 1);
    if (this.selectedFiles.length === 0) {
      this.result = null;
    }
  }

  private checkFile(file: File): boolean {
    const allowed = ['pdf', 'docx', 'rtf', 'xlsx', 'xls'];
    const ext = file.name.split('.').pop()?.toLowerCase() || '';

    if (!allowed.includes(ext)) {
      this.snackBar.open('Invalid file type! Only PDF, Word, Excel, and RTF are allowed.', 'Close', { duration: 5000 });
      return false;
    }

    if (file.size > 10 * 1024 * 1024) {
      this.snackBar.open('File too large! Max size is 10MB.', 'Close', { duration: 5000 });
      return false;
    }

    return true;
  }

  async analyze() {
    if (this.selectedFiles.length === 0) return;

    this.analyzing = true;
    this.isCancelled = false;
    this.processedCount = 0;
    this.analyzingSummary = false;
    let combinedText = '';
    let filenames: string[] = [];

    try {
      for (const file of this.selectedFiles) {
        if (this.isCancelled) {
          this.snackBar.open('Analysis cancelled by user.', 'Close', { duration: 3000 });
          break;
        }

        this.currentProcessingFile = file.name;
        const res = await this.documentService.analyze(file, this.selectedTone).toPromise();
        if (res) {
          const cleanName = file.name.replace(/[^\w\s\.-]/gi, '');
          combinedText += `\n--- Document: ${cleanName} ---\n${res.extractedText}\n`;
          filenames.push(cleanName);
          this.processedCount++;
        }
      }

      if (!this.isCancelled && combinedText) {
        this.analyzingSummary = true;
        this.documentService.summarize(combinedText, this.selectedTone).subscribe({
          next: (summaryRes) => {
            this.result = {
              filename: filenames.join(', '),
              extractedText: combinedText,
              summary: summaryRes.summary,
              takeaways: summaryRes.takeaways
            };
            this.analyzing = false;
            this.analyzingSummary = false;
            this.snackBar.open(`Processed ${this.processedCount} documents!`, 'Close', { duration: 3000 });
          },
          error: (err) => {
            this.analyzing = false;
            this.analyzingSummary = false;
            this.snackBar.open('Error generating final analysis.', 'Close', { duration: 5000 });
          }
        });
      }
    } catch (err: any) {
      if (this.isCancelled) return;
      this.analyzing = false;
      this.analyzingSummary = false;
      const errMsg = err.error?.detail || err.message || 'Error during batch analysis';
      this.snackBar.open(`Error: ${errMsg}`, 'Close', { duration: 10000 });
    }
  }

  cancelAnalysis() {
    this.isCancelled = true;
    this.analyzing = false;
  }

  summarize() {
    if (!this.result) return;
    this.analyzing = true;
    this.documentService.summarize(this.result.extractedText, this.selectedTone).subscribe({
      next: (res) => {
        if (this.result) {
          this.result.summary = res.summary;
          this.result.takeaways = res.takeaways;
        }
        this.analyzing = false;
        this.snackBar.open('Analysis refreshed!', 'Close', { duration: 3000 });
      },
      error: (err) => {
        this.analyzing = false;
        this.snackBar.open('Error refreshing analysis.', 'Close', { duration: 3000 });
      }
    });
  }

  askQuestion() {
    if (!this.question || !this.result) return;

    this.asking = true;
    this.answer = 'Thinking...';
    this.documentService.askQuestion(this.result.extractedText, this.question).subscribe({
      next: (res: { answer: string }) => {
        this.answer = res.answer;
        this.asking = false;
      },
      error: (err: any) => {
        console.error('[App] Q&A Error:', err);
        this.asking = false;
        this.answer = '';
        this.snackBar.open('Error getting answer. Check console logs.', 'Close', { duration: 3000 });
      }
    });
  }

  copySummary() {
    if (!this.result?.summary) return;
    navigator.clipboard.writeText(this.result.summary).then(() => {
      this.snackBar.open('Summary copied to clipboard!', 'Close', { duration: 2000 });
    });
  }

  async exportPDF() {
    if (!this.result) return;
    const { jsPDF } = await import('jspdf');
    const doc = new jsPDF();

    doc.setFontSize(18);
    doc.text('SmartDoc AI Analysis Report', 10, 10);

    doc.setFontSize(12);
    doc.text(`File: ${this.result.filename}`, 10, 20);
    doc.text(`Tone: ${this.selectedTone}`, 10, 30);

    doc.setFontSize(14);
    doc.text('Summary:', 10, 40);
    doc.setFontSize(10);

    const splitSummary = doc.splitTextToSize(this.result.summary, 180);
    doc.text(splitSummary, 10, 50);

    doc.save(`${this.result.filename}_analysis.pdf`);
  }

  exportTXT() {
    if (!this.result) return;
    const content = `SmartDoc AI Report\nFile: ${this.result.filename}\n\nSUMMARY:\n${this.result.summary}\n\nEXECUTIVE TAKEAWAYS:\n- ${this.result.takeaways.join('\n- ')}`;
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${this.result.filename}_report.txt`;
    a.click();
  }

}
