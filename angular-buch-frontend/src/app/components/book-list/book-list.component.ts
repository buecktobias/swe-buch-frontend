import { Component, OnInit } from '@angular/core';
import { BuchEntity } from '../../graphql/entities';
import { BookViewComponent } from '../book-view/book-view.component';
import { BookService } from '../../services/books/book.service';

@Component({
  selector: 'app-book-list',
  standalone: true,
  imports: [BookViewComponent],
  templateUrl: './book-list.component.html',
  styleUrl: './book-list.component.scss',
})
export class BookListComponent implements OnInit {
  books: BuchEntity[] = [];

  constructor(private bookService: BookService) {}

  ngOnInit(): void {
    this.bookService
      .getAllBooks()
      .subscribe((result: { data: { buecher: BuchEntity[] } }) => {
        this.books = result.data.buecher;
      });
  }
}