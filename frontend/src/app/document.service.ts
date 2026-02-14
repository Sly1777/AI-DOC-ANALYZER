import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface AnalysisResult {
  filename: string;
  summary: string;
  takeaways: string[];
  extractedText: string;
}

@Injectable({
  providedIn: 'root'
})
export class DocumentService {
  private apiUrl = 'http://localhost:8081/api/documents';

  constructor(private http: HttpClient) { }

  analyze(file: File, tone: string = 'executive'): Observable<AnalysisResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tone', tone);
    return this.http.post<AnalysisResult>(`${this.apiUrl}/analyze`, formData);
  }

  askQuestion(text: string, question: string): Observable<{ answer: string }> {
    return this.http.post<{ answer: string }>(`${this.apiUrl}/ask`, { text, question });
  }

  summarize(text: string, tone: string = 'executive'): Observable<{ summary: string, takeaways: string[] }> {
    return this.http.post<{ summary: string, takeaways: string[] }>(`${this.apiUrl}/summarize`, { text, tone });
  }
}
