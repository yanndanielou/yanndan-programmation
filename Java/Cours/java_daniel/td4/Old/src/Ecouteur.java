import java.awt.event.*;

public class Ecouteur extends MouseAdapter // implements MouseListener oblige � red�finir tt les m�thodes  
{
	String Title;
		
	public Ecouteur(String Title)
	{
		this.Title = Title;
	}
	
	public void mousePressed(MouseEvent e)
	{
		System.out.println("Fenetre " + Title + " : Cliqu�, posx = " + e.getX() + ", posy = " + e.getY());
	}
	
	public void mouseReleased(MouseEvent e)
	{
		System.out.println("Fenetre " + Title + " : Relach�, posx = " + e.getX() + ", posy = " + e.getY());
	}
}
