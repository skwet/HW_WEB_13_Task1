from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.schemas import ContactBase,ContactResponse,ContactUpdate
from src.repository import contacts
from src.services.auth import auth_service
from src.database.models import User

router = APIRouter(prefix='/contacts', tags=["contacts"])

@router.get('/', response_model=List[ContactResponse],dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contacts(db: Session = Depends(get_db),current_user: User = Depends(auth_service.get_current_user)):
    contacts_l = await contacts.get_contacts(db,current_user)
    return contacts_l

@router.get('/{contact_id}', response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def read_contact(contact_id: int, db: Session = Depends(get_db),current_user: User = Depends(auth_service.get_current_user)):
    contact = await contacts.get_contact(contact_id,current_user,db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.post('/', response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(body: ContactBase, db: Session = Depends(get_db),current_user: User = Depends(auth_service.get_current_user)):
    return await contacts.create_contact(body, current_user, db)

@router.patch('/{contact_id}', response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def update_cont(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    contact = await contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@router.delete('/{contact_id}', response_model=ContactResponse,dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    tag = await contacts.delete_contact(contact_id,current_user,db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return tag

@router.get('/birthdays/',response_model=List[ContactResponse],dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def get_birth(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    birthday = await contacts.get_birthdays(current_user,db)

    if birthday:
        return birthday
    else:
        return []
    
@router.get('/search/',response_model=List[ContactResponse],dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def search_contacts(query: str, current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    search_results = await contacts.find_contact(query, current_user, db)
    if not search_results:
        return []
    return search_results