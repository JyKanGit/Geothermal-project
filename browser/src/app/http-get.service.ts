import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class HttpGetService {

  constructor(private http: HttpClient) {}
  
  getData(url: string): Observable<any> {
    // enable to use dev server with ng serve
    // url = "http://<ip address>:<port>" + url;

    return this.http.get(url);
  }
}
